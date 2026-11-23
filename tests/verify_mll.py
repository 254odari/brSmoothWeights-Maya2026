#!/usr/bin/env python3

import argparse
import struct
import sys
from pathlib import Path


class VerificationError(Exception):
    pass


def u16(data, offset):
    return struct.unpack_from("<H", data, offset)[0]


def u32(data, offset):
    return struct.unpack_from("<I", data, offset)[0]


def rva_to_offset(data, sections, rva):
    for virtual_address, virtual_size, raw_size, raw_offset in sections:
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_offset + rva - virtual_address
    raise VerificationError(f"RVA 0x{rva:X} is not mapped by any PE section")


def verify_mll(path):
    data = path.read_bytes()
    if len(data) < 64 or data[:2] != b"MZ":
        raise VerificationError("file does not have an MS-DOS header")

    pe_offset = u32(data, 0x3C)
    if pe_offset + 24 > len(data) or data[pe_offset:pe_offset + 4] != b"PE\0\0":
        raise VerificationError("file does not have a PE header")

    machine = u16(data, pe_offset + 4)
    if machine != 0x8664:
        raise VerificationError(f"expected AMD64 machine 0x8664, found 0x{machine:X}")

    section_count = u16(data, pe_offset + 6)
    optional_size = u16(data, pe_offset + 20)
    optional_offset = pe_offset + 24
    if optional_offset + optional_size > len(data):
        raise VerificationError("optional header extends beyond the file")
    if u16(data, optional_offset) != 0x20B:
        raise VerificationError("expected a PE32+ optional header")

    section_offset = optional_offset + optional_size
    sections = []
    for index in range(section_count):
        offset = section_offset + index * 40
        if offset + 40 > len(data):
            raise VerificationError("section table extends beyond the file")
        virtual_size = u32(data, offset + 8)
        virtual_address = u32(data, offset + 12)
        raw_size = u32(data, offset + 16)
        raw_offset = u32(data, offset + 20)
        sections.append((virtual_address, virtual_size, raw_size, raw_offset))

    export_rva = u32(data, optional_offset + 112)
    if export_rva == 0:
        raise VerificationError("file has no export directory")

    export_offset = rva_to_offset(data, sections, export_rva)
    if export_offset + 40 > len(data):
        raise VerificationError("export directory extends beyond the file")

    name_count = u32(data, export_offset + 24)
    names_rva = u32(data, export_offset + 32)
    if name_count == 0 or names_rva == 0:
        raise VerificationError("file exports no names")

    names_offset = rva_to_offset(data, sections, names_rva)
    if names_offset + name_count * 4 > len(data):
        raise VerificationError("export name table extends beyond the file")

    exports = set()
    for index in range(name_count):
        name_rva = u32(data, names_offset + index * 4)
        name_offset = rva_to_offset(data, sections, name_rva)
        name_end = data.find(b"\0", name_offset)
        if name_end < 0:
            raise VerificationError("unterminated export name")
        exports.add(data[name_offset:name_end].decode("ascii"))

    required = {"initializePlugin", "uninitializePlugin"}
    missing = required - exports
    if missing:
        raise VerificationError(f"missing required exports: {', '.join(sorted(missing))}")

    print(f"PASS: {path}")
    print("PE32+ machine: AMD64 (0x8664)")
    print("Required exports: initializePlugin, uninitializePlugin")


def main():
    parser = argparse.ArgumentParser(description="Verify a Maya 2026 Windows plug-in binary.")
    parser.add_argument("mll", type=Path)
    args = parser.parse_args()

    try:
        verify_mll(args.mll)
    except (OSError, struct.error, UnicodeDecodeError, VerificationError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
