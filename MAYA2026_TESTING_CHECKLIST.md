# Maya 2026 testing checklist

Status date: 2026-11-24.

## Current verification status

| Check | Status | Evidence / limitation |
| --- | --- | --- |
| Upstream source and resource audit | Passed | Baseline `bb017e67c2bf7ca03cb626cacfa2ca58b3a66bd8`; see [MAYA2026_PORTING_AUDIT.md](MAYA2026_PORTING_AUDIT.md). |
| Maya 2026 API/signature inspection | Passed | Checked against the installed Maya 2026 headers. |
| Ported-source syntax compilation | Passed | All three translation units compiled with MSVC 19.51 and Maya 2026 headers. This is not the official VS2022 toolchain. |
| CMake configuration | Passed with limitation | CMake 4.4.5 generated NMake build files and found every SDK component. Static-library compiler probes were necessary because the local CRT import libraries are missing. |
| CMake compilation | Passed | All three translation units compiled through the generated build. |
| Local `.mll` link | Blocked | Local VS2026 Build Tools cannot find `msvcprt.lib`. No Maya 2026 `.mll` was produced locally. |
| Workflow YAML and PE verifier static checks | Passed | YAML parsed; the verifier accepted the upstream Maya 2025 x64 binary and rejected a non-PE file. |
| GitHub Actions VS2022 build | Not run | Requires the workflow to be pushed and executed on GitHub. |
| Maya 2026 load/unload and registration | Not tested | Requires a successfully linked Maya 2026 binary. |
| Smoothing, transfer, UI, and numerical behavior | Not tested | Requires interactive Maya 2026 testing. |

## Test record

Complete this section for each tested configuration:

- Maya version/update:
- Windows version:
- CPU / GPU / Viewport 2 driver:
- Binary source and commit:
- Test scene:
- Tester and date:
- Overall result:

## 1. Installation and loading

- [ ] Install the `.mod` file and module content using [MAYA2026_INSTALLATION.md](MAYA2026_INSTALLATION.md).
- [ ] Start Maya 2026 and confirm there are no startup errors.
- [ ] Open the Skin menu and confirm lazy plug-in loading.
- [ ] Confirm both **Paint Smooth Weights Tool** and **Paint Transfer Weights Tool** appear once.
- [ ] Confirm their option boxes open without errors.
- [ ] Load directly and confirm `pluginInfo -loaded brSmoothWeights` returns true.
- [ ] Confirm `brSmoothWeightsContext` and `brTransferWeightsContext` are registered.
- [ ] Confirm `brSmoothWeightsCmd` and `brTransferWeightsCmd` are registered and their syntax/help is available.
- [ ] Confirm the reported plug-in path is the Maya 2026 `.mll`, not an upstream 2025 binary.
- [ ] Run `python tests/verify_mll.py <path-to-brSmoothWeights.mll>` and confirm AMD64 plus both required exports.

Suggested Python load check:

```python
import maya.cmds as cmds
cmds.loadPlugin("brSmoothWeights")
assert cmds.pluginInfo("brSmoothWeights", query=True, loaded=True)
```

## 2. Unloading and reloading

- [ ] Exit both paint tools before unloading.
- [ ] Unload the plug-in and confirm `pluginInfo -loaded brSmoothWeights` returns false.
- [ ] Confirm both context commands are no longer registered.
- [ ] Reload the plug-in and confirm both context commands register again.
- [ ] Confirm the Skin menu has no duplicate entries after reload.
- [ ] Save a scene with a tool active, reopen it, and confirm there is no stale-context error.
- [ ] Restart Maya and confirm the module is discovered again.

## 3. Smoothing behavior

Use a simple skinned grid or polygon mesh with at least two influences and known starting weights.

- [ ] Paint a smooth stroke and confirm only intended vertices change.
- [ ] Confirm weights remain normalized when normalization is enabled.
- [ ] Confirm flood mode affects the intended selection.
- [ ] Confirm Affect Selected changes the affected vertex set as expected.
- [ ] Confirm brush size, strength, curve, range, tolerance, undersampling, and oversampling controls alter the result coherently.
- [ ] Confirm fraction oversampling behaves consistently with the original tool.
- [ ] Confirm depth and depth-start select the intended surface intersections.
- [ ] Confirm volume mode and keep-shells-together behave consistently on a two-shell test mesh.
- [ ] Confirm boundary/opposite-face handling does not skip or crash on a test seam.
- [ ] Confirm brush and range drawing work in Viewport 2.
- [ ] Confirm in-view messages and option-window controls work.
- [ ] Undo and redo a stroke and confirm the exact weights and selection are restored.
- [ ] Compare a fixed scene and stroke against the upstream build where available; record any numerical differences.

## 4. Transfer behavior

- [ ] Select valid source and destination influences.
- [ ] Paint a transfer stroke and confirm weight moves from source to destination.
- [ ] Confirm Replace and Reverse produce their documented effects.
- [ ] Confirm flood mode transfers across the intended selection.
- [ ] Confirm source/destination influence labels and locking state display correctly.
- [ ] Confirm depth, volume, shell, falloff, brush, and oversampling controls work consistently with smoothing.
- [ ] Confirm locked destination influences are respected.
- [ ] Confirm unset source/destination influences fail safely rather than crashing or accessing invalid array indices.
- [ ] Undo and redo a transfer stroke and confirm the exact weights are restored.
- [ ] Compare a fixed scene and stroke against the upstream build where available.

## 5. Influences and skinCluster settings

- [ ] Lock and unlock influences from the influence list.
- [ ] Confirm smoothing respects locked influences.
- [ ] Confirm Ignore Lock bypasses locks only when enabled.
- [ ] Confirm transfer respects source/destination lock rules.
- [ ] Test Maintain Max Influences with a low max-influence value.
- [ ] Test normalized and non-normalized skinClusters.
- [ ] Test a skinCluster with sparse or zero weights.
- [ ] Test multiple influences with long or non-ASCII names.
- [ ] Confirm failed or missing plug reads do not overwrite existing defaults.

## 6. Mesh and selection compatibility

- [ ] Test a mesh with a valid skinCluster.
- [ ] Test a mesh without a skinCluster and confirm a clean failure.
- [ ] Test an intermediate shape and confirm the original selection rules are preserved.
- [ ] Test multiple selected meshes with separate skinClusters.
- [ ] Test multiple selected meshes with different vertex counts.
- [ ] Test component selections and full-object selections.
- [ ] Test non-manifold, disconnected, and high-density meshes.
- [ ] Test transformed meshes and non-uniform scaling.
- [ ] Confirm no out-of-range component or influence access occurs.

## 7. Error handling and stability

- [ ] Paint outside geometry and confirm no unnecessary error spam or crash.
- [ ] Deselect all geometry while the tool is active.
- [ ] Delete or disconnect a skinCluster while the tool is active.
- [ ] Set brush size/range to zero and confirm the tool does not crash.
- [ ] Test invalid context flags and confirm Maya reports syntax errors cleanly.
- [ ] Attempt to load a non-x64 or non-Maya-2026 binary and confirm it fails without crashing.
- [ ] Remove the `.mll` after module registration and confirm the error is clear.
- [ ] Run a repeated-stroke stress test and monitor memory use and Maya responsiveness.
- [ ] Review Maya's Script Editor and output log for C++ exceptions, assertions, or dependency errors.

## 8. Installer and packaging

- [ ] Build or place the 2026 `.mll` in a distribution folder named `brSmoothWeights`.
- [ ] Run `dragDropInstaller.py` in Maya 2026 and confirm the EULA renders UTF-8 text.
- [ ] Confirm the installer detects the 2026 Windows plug-in.
- [ ] Confirm the generated `.mod` file contains the Maya 2026 Windows block.
- [ ] Install to paths without spaces and confirm loading.
- [ ] Install to a path with spaces and confirm loading; record any uninstall-parser limitation.
- [ ] Confirm no Autodesk SDK files, credentials, build caches, or test artifacts are committed.
- [ ] Confirm the GitHub Actions artifact contains only the verified `.mll`.

## 9. Final acceptance

- [ ] Hosted VS2022 build passes.
- [ ] PE verification passes on the newly built Maya 2026 binary.
- [ ] All loading and registration checks pass.
- [ ] All smoothing and transfer checks pass.
- [ ] Undo/redo and restart/reload checks pass.
- [ ] No new C++ or MEL errors appear in Maya's output.
- [ ] Any remaining differences from upstream are documented rather than hidden.
