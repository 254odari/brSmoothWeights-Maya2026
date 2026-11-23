# Maya 2026 Windows installation

This port targets Autodesk Maya 2026, Windows 64-bit, and the Maya 2026 C++ SDK. It preserves the original `brSmoothWeights` and `brTransferWeights` tools, MEL resources, lazy-loading workflow, MIT license, and Ingo Clemens / brave rabbit credits.

Build and runtime status is tracked in [MAYA2026_TESTING_CHECKLIST.md](MAYA2026_TESTING_CHECKLIST.md). Do not treat the plug-in as runtime-validated until the Maya 2026 checks in that document pass.

## Requirements

For building:

- Visual Studio 2022 Build Tools 17.8.3 or newer with the x64 C++ workload. The full Visual Studio IDE is not required.
- CMake 3.27.3 or newer.
- The official Autodesk Maya 2026 DevKit, or a Maya 2026 installation containing `include/maya`, `include/oneapi`, and the Windows x64 import libraries.
- The oneTBB headers and `tbb12.lib` shipped with Maya 2026.

For installation:

- Autodesk Maya 2026 on Windows 64-bit.
- Write access to a directory on Maya's `MAYA_MODULE_PATH`.

Only obtain Autodesk SDK files from Autodesk. Do not commit SDK headers, import libraries, credentials, or downloaded DevKit archives to this repository.

## Build locally

Run these commands from an x64 Visual Studio 2022 developer shell:

```powershell
cmake -S . -B build -G "Visual Studio 17 2022" -A x64 `
  -DMAYA_LOCATION="C:/Program Files/Autodesk/Maya2026"
cmake --build build --config Release --parallel
cmake --install build --config Release --prefix "$PWD/package/modules/brSmoothWeights"
python tests/verify_mll.py package/modules/brSmoothWeights/plug-ins/win64/2026/brSmoothWeights.mll
```

`MAYA_LOCATION` may point either to a Maya 2026 installation or to the root of an extracted official DevKit. CMake fails with a clear error if the required headers or libraries are absent.

The install step creates:

```text
package/modules/brSmoothWeights/plug-ins/win64/2026/brSmoothWeights.mll
```

The PE verifier checks that the binary is PE32+ AMD64 and exports `initializePlugin` and `uninitializePlugin`. It does not replace loading or behavior tests inside Maya.

## GitHub Actions build

[.github/workflows/build-maya2026-windows.yml](.github/workflows/build-maya2026-windows.yml) runs on `windows-2022` and:

1. Verifies that VS2022 17.8.3+ and CMake 3.27.3+ are available.
2. Downloads the pinned official Autodesk Maya 2026 Update 3 DevKit over HTTPS into runner temporary storage.
3. Configures, builds, and installs the plug-in with the VS2022 x64 toolchain.
4. Verifies the binary architecture and required exports.
5. Uploads only `brSmoothWeights.mll` as the `brSmoothWeights-Maya2026-win64` artifact.
6. Removes the downloaded DevKit even when the job fails.

Only artifacts from successful runs should be marked build-validated. The current verified run is [45275333759](https://github.com/254odari/brSmoothWeights-Maya2026/actions/runs/45275333759) at commit `228227f`; its artifact passed independent PE verification and an isolated Maya 2026.2 load/unload/reload smoke test. Interactive behavior remains unverified.

## Manual module installation

### 1. Stage the module

Choose a permanent module content directory. The following example uses `C:/brSmoothWeights-Maya2026/modules/brSmoothWeights`:

```powershell
$moduleRoot = "C:/brSmoothWeights-Maya2026/modules/brSmoothWeights"
cmake --install build --config Release --prefix $moduleRoot
Copy-Item -Path modules/brSmoothWeights/scripts,modules/brSmoothWeights/icons -Destination $moduleRoot -Recurse
```

If using a downloaded workflow artifact instead of a local build, create `$moduleRoot/plug-ins/win64/2026`, copy `brSmoothWeights.mll` there, and then copy the repository's `scripts` and `icons` directories into `$moduleRoot`.

The resulting layout must be:

```text
brSmoothWeights/
  icons/
  scripts/
  plug-ins/
    win64/
      2026/
        brSmoothWeights.mll
```

### 2. Register the module

Find a directory already listed by Maya's `MAYA_MODULE_PATH`. In Maya's Python editor:

```python
import maya.cmds as cmds
print(cmds.getenv("MAYA_MODULE_PATH"))
```

Create `brSmoothWeights.mod` in one of those directories with the following content, replacing the final path with the absolute path to the staged `brSmoothWeights` directory:

```text
+ MAYAVERSION:2026 PLATFORM:win64 brSmoothWeights any C:/brSmoothWeights-Maya2026/modules/brSmoothWeights
plug-ins: plug-ins/win64/2026
[r] icons: icons
[r] scripts: scripts
```

Use forward slashes in the `.mod` file. Restart Maya after creating or changing it.

### 3. Verify and launch

Normal workflow:

1. Start Maya 2026 in GUI mode.
2. Open the Skin menu.
3. Confirm that the plug-in loads lazily and the menu contains **Paint Smooth Weights Tool** and **Paint Transfer Weights Tool**.
4. Select a skinned mesh and launch either tool.

Direct verification in Maya's Python editor:

```python
import maya.cmds as cmds
cmds.loadPlugin("brSmoothWeights")
print(cmds.pluginInfo("brSmoothWeights", query=True, loaded=True))
print(cmds.pluginInfo("brSmoothWeights", query=True, path=True))
```

Direct MEL launch fallback:

```mel
loadPlugin brSmoothWeights;
source brSmoothWeightsToolCtx;
brSmoothWeightsToolCtx;

source brTransferWeightsToolCtx;
brTransferWeightsToolCtx;
```

## Existing drag-and-drop installer

The original installer workflow is preserved:

1. Build the Maya 2026 binary and copy it to `modules/brSmoothWeights/plug-ins/win64/2026/brSmoothWeights.mll`.
2. Keep the distribution folder named `brSmoothWeights`; the installer derives the module name from that folder name.
3. Run `dragDropInstaller.py` in Maya 2026 as described in the original installation guide.
4. Restart Maya and use the Skin menu.

`resources/module_template.mod` now contains the Maya 2026 Windows entry. The installer reads the MIT license as UTF-8 text for Maya's Python 3 `scrollField` API.

## Unload and reload

Exit both paint tools before unloading the plug-in:

```python
import maya.cmds as cmds
cmds.unloadPlugin("brSmoothWeights")
cmds.loadPlugin("brSmoothWeights")
```

If Maya reports that the plug-in is in use, return to the normal move/select context or restart Maya. After reload, confirm that the Skin menu does not contain duplicate tool entries.

## Troubleshooting

- **Module not found:** confirm the `.mod` file is on `MAYA_MODULE_PATH`, the final path is absolute, and `MAYAVERSION:2026` and `PLATFORM:win64` match the session.
- **Plug-in not found:** confirm the `.mll` is under `plug-ins/win64/2026` relative to the module root.
- **Missing DLL or dependency error:** use a Maya 2026 x64 binary built with the dynamic MSVC runtime and Maya's bundled `tbb12.lib`; do not substitute the upstream Maya 2025 binary.
- **Menu items absent:** confirm GUI mode is active, the module's `scripts/userSetup.py` was discovered, and the Skin menu was opened after startup. Batch mode intentionally skips menu creation.
- **EULA displays bytes instead of text:** use the updated `dragDropInstaller.py` from this port.
- **SDK unavailable:** obtain the official Maya 2026 DevKit from [Autodesk's Maya API / SDK page](https://aps.autodesk.com/developer/overview/maya-api). The workflow does not use third-party SDK mirrors.
