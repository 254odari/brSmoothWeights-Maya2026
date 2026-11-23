# brSmoothWeights & brTransferWeights
Tools for smoothing and transferring skin weights between influences in Autodesk Maya.

Even though the tool is Open Source we appreciate if you would consider support for continued development via [Gumroad](https://braverabbit.gumroad.com/l/brSmoothWeightsMaya)
Thank you!

## Maya 2026 Windows port

This repository ports the original tools to Autodesk Maya 2026 on Windows 64-bit while preserving both tools, their algorithms, MEL resources, lazy-loading workflow, MIT license, and original credits.

Current status: the native sources pass Maya 2026 syntax checks and CMake compilation locally. A complete local link is blocked by missing CRT import libraries in the available Build Tools installation; the hosted VS2022 build and Maya 2026 runtime behavior remain unverified. See [MAYA2026_TESTING_CHECKLIST.md](MAYA2026_TESTING_CHECKLIST.md) for the exact status.

### Build

Requirements:

- Visual Studio 2022 Build Tools 17.8.3+ with x64 C++ support
- CMake 3.27.3+
- Official Maya 2026 DevKit or a Maya 2026 installation with headers and import libraries

From an x64 VS2022 developer shell:

```powershell
cmake -S . -B build -G "Visual Studio 17 2022" -A x64 `
  -DMAYA_LOCATION="C:/Program Files/Autodesk/Maya2026"
cmake --build build --config Release --parallel
cmake --install build --config Release --prefix "$PWD/package/modules/brSmoothWeights"
python tests/verify_mll.py package/modules/brSmoothWeights/plug-ins/win64/2026/brSmoothWeights.mll
```

The GitHub Actions workflow [build-maya2026-windows.yml](.github/workflows/build-maya2026-windows.yml) uses `windows-2022`, downloads the official Autodesk DevKit ephemerally, verifies the x64 exports, uploads only the `.mll`, and removes the SDK files afterward.

### Install and launch

Follow [MAYA2026_INSTALLATION.md](MAYA2026_INSTALLATION.md) for local builds, workflow artifacts, manual `.mod` installation, and the existing drag-and-drop installer.

The normal workflow is unchanged: install the module, restart Maya, open the Skin menu to load the plug-in lazily, then choose **Paint Smooth Weights Tool** or **Paint Transfer Weights Tool**.

## Video
[brSmoothWeights on YouTube](https://youtu.be/cT5zW-byR_c)

## Installation
Installation is easy with the included installer.

[Easy Install](https://github.com/IngoClemens/brSmoothWeights/wiki/Installation)

For Maya 2026 on Windows, use the [Maya 2026 installation guide](MAYA2026_INSTALLATION.md).

## Getting Started
Visit the [Quick Guide](https://github.com/IngoClemens/brSmoothWeights/wiki/Quick-Guide) for basic tool usage.

See the [Wiki](https://github.com/IngoClemens/brSmoothWeights/wiki) for full details.

## Audit and testing

- [Maya 2026 porting audit](MAYA2026_PORTING_AUDIT.md)
- [Maya 2026 testing checklist](MAYA2026_TESTING_CHECKLIST.md)

## Credits and license

Original `brSmoothWeights` and `brTransferWeights` tools by [Ingo Clemens / brave rabbit](https://braverabbit.com). This port preserves the [MIT license](LICENSE) and original attribution.
