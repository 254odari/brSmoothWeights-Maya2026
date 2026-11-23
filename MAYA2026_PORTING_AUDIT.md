# Maya 2026 Porting Audit

- **Audit date:** 2026-11-24
- **Target:** Autodesk Maya 2026, Windows x64
- **Upstream audited:** `id3a-pipeline/brSmoothWeights` at `bb017e67c2bf7ca03cb626cacfa2ca58b3a66bd8`
- **Published destination:** [`254odari/brSmoothWeights-Maya2026`](https://github.com/254odari/brSmoothWeights-Maya2026)

## 1. Scope and status

This report began before implementation changes. Sections 2–11 document the audit findings and resulting design for the upstream source, headers, MEL scripts, Python installer, module template, documentation, resources, and packaged build-environment archives. Sections 12–13 record the implementation and current validation. Native API signatures were checked against the installed Maya 2026 headers at `C:/Program Files/Autodesk/Maya2026/include`.

The hosted VS2022 build, independent PE verification, and isolated Maya 2026.2 load/unload/reload smoke test passed. No interactive UI, painting, numerical-comparison, or stress test has been performed.

## 2. Repository inventory

### Native source and headers

| File | Role |
| --- | --- |
| `source/pluginMain.cpp` | Plug-in registration and deregistration for both tools. |
| `source/smoothWeightsTool.h` | `smoothWeightsTool`, `smoothWeightsContext`, and `smoothWeightsContextCmd` declarations. |
| `source/smoothWeightsTool.cpp` | Smoothing command/context, brush, flood, mesh traversal, weight read/write, undo/redo, and Viewport 2 drawing. |
| `source/transferWeightsTool.h` | `transferWeightsTool`, `transferWeightsContext`, and `transferWeightsContextCmd` declarations. |
| `source/transferWeightsTool.cpp` | Weight-transfer command/context, source/destination influence handling, brush, flood, mesh traversal, undo/redo, and Viewport 2 drawing. |

### Maya scripts and resources

- `modules/brSmoothWeights/scripts/brSmoothWeightsCreateMenuItems.mel`
- `modules/brSmoothWeights/scripts/brSmoothWeightsInfluenceList.mel`
- `modules/brSmoothWeights/scripts/brSmoothWeightsProperties.mel`
- `modules/brSmoothWeights/scripts/brSmoothWeightsProperties.res.mel`
- `modules/brSmoothWeights/scripts/brSmoothWeightsShowInViewMessage.mel`
- `modules/brSmoothWeights/scripts/brSmoothWeightsToolCtx.mel`
- `modules/brSmoothWeights/scripts/brSmoothWeightsValues.mel`
- `modules/brSmoothWeights/scripts/brTransferWeightsInfluenceList.mel`
- `modules/brSmoothWeights/scripts/brTransferWeightsProperties.mel`
- `modules/brSmoothWeights/scripts/brTransferWeightsProperties.res.mel`
- `modules/brSmoothWeights/scripts/brTransferWeightsShowInViewMessage.mel`
- `modules/brSmoothWeights/scripts/brTransferWeightsToolCtx.mel`
- `modules/brSmoothWeights/scripts/brTransferWeightsValues.mel`
- `modules/brSmoothWeights/scripts/userSetup.py`
- SVG and PNG icon sets for both tools under `modules/brSmoothWeights/icons/`.
- Prebuilt upstream binaries for Linux, macOS, and Windows through Maya 2025. There is no Maya 2026 binary.

### Build, installation, and documentation

- `README.md`
- `LICENSE`
- `versions.md`
- `installationGuide.html`
- `dragDropInstaller.py`
- `resources/module_template.mod`
- `source/env/README.md`
- `source/env/versions/1.0.0/linux.zip`
- `source/env/versions/1.0.0/macOS.zip`
- `source/env/versions/1.0.0/win64.zip`

There is no root `CMakeLists.txt`, Visual Studio project, solution, or maintained current build script. `source/env/README.md` describes a Visual Studio Express 2013 project and explicitly warns that the archived build environments can contain stale source.

## 3. Existing functionality

### brSmoothWeights

The plug-in registers `brSmoothWeightsContext` and its tool command `brSmoothWeightsCmd`. The MEL launcher `brSmoothWeightsToolCtx` creates the context and selects it. Features include:

- Paint and flood smoothing.
- Adjustable brush size, strength, curve, range, depth, depth start, tolerance, oversampling, undersampling, and fraction oversampling.
- Surface and volume modes.
- Selected-vertex-only mode.
- Influence locking and ignore-lock mode.
- Shell-connectivity and boundary handling.
- Undo/redo of affected weights and selection/highlight state.
- Influence-list UI, tool settings, enter/exit commands, in-view messages, and Viewport 2 brush drawing.

### brTransferWeights

The plug-in registers `brTransferWeightsContext` and its tool command `brTransferWeightsCmd`. The MEL launcher `brTransferWeightsToolCtx` creates the context and selects it. Features include:

- Paint and flood transfer between source and destination influences.
- Replace and reverse modes.
- Shared brush, falloff, depth, volume, selection, shell, and influence-lock behavior.
- Undo/redo of transferred weights and selection/highlight state.
- Influence-list UI, tool settings, enter/exit commands, in-view messages, and Viewport 2 brush drawing.

The original numerical algorithms are retained as the porting baseline. This audit does not propose replacing them with simplified implementations.

## 4. Maya API dependencies

The native code uses:

- Core/DG/DAG: `MStatus`, `MObject`, `MString`, `MFn`, `MPoint`, `MFloatPoint`, `MVector`, `MFloatVector`, `MMatrix`, `MColor`, Maya array types, `MDagPath`, `MDagPathArray`, `MSelectionList`, `MGlobal`, `MPlug`, `MFnDependencyNode`, and `MFnDagNode`.
- Commands/events/tools: `MArgList`, `MArgDatabase`, `MArgParser`, `MSyntax`, `MEvent`, `MPxToolCommand`, `MPxContext`, and `MPxContextCommand`.
- Mesh/geometry: `MFnMesh`, `MFnSingleIndexedComponent`, `MFnCamera`, `MItDependencyGraph`, `MItSelectionList`, `MItMeshVertex`, `MItMeshEdge`, `MItMeshPolygon`, `MMeshIntersector`, and `MPointOnMesh`.
- Skinning: `MFnSkinCluster` from OpenMayaAnim.
- UI/Viewport 2: `M3dView`, `MCursor`, `MToolsInfo`, `MHWRender::MUIDrawManager`, and `MHWRender::MFrameContext`.
- Registration: `MFnPlugin`.

`MItGeometry` is not directly used. Maya 2026 provides `MItMeshVertex` as a standalone class, so no `MItGeometry` migration is required.

Expected Windows import libraries are `Foundation.lib`, `OpenMaya.lib`, `OpenMayaUI.lib`, `OpenMayaAnim.lib`, `OpenMayaRender.lib`, and the Maya-bundled `tbb12.lib`.

## 5. Maya 2026 compatibility findings

### 5.1 Verified compile check

All three unchanged `.cpp` files passed a syntax-only compile against the installed Maya 2026 headers using MSVC 19.51 (Visual Studio 2026 Build Tools) with `/std:c++17 /EHsc /MD /DNT_PLUGIN`.

A baseline link then failed with:

```text
LINK : fatal error LNK1104: cannot open file 'msvcprt.lib'
```

The installed Visual Studio 2026 Build Tools contain `cl.exe` but not the x64 CRT import libraries or Windows SDK import libraries. This is a local toolchain-installation blocker, not a source compile error. The official Maya 2026 Windows compiler requirement is Visual Studio 2022 17.8.3 or higher; a GitHub `windows-2022` runner is the preferred validation environment.

### 5.2 API and source findings

| Severity | Finding | Evidence | Proposed action |
| --- | --- | --- | --- |
| Warning | `MFnMesh::allIntersections` accepts `MFloatPoint`/`MFloatVector` in Maya 2026. The existing `MPoint`/`MVector` arguments compile through non-explicit Maya conversion constructors. | `source/smoothWeightsTool.cpp:1636`, `source/transferWeightsTool.cpp:1608`; `MFloatPoint.h:44`, `MFloatVector.h:43`. | Not a Maya 2026 compile blocker. Keep the call unchanged for the minimal port; explicit float locals are optional clarification only. |
| Warning | No-argument `MPlug::asInt()` and `MPlug::asBool()` are deprecated. | `source/smoothWeightsTool.cpp:1522,1525,1528,1583`; `source/transferWeightsTool.cpp:1499,1555`. | Use the status-taking overloads and handle failed plug reads without changing defaults. |
| Warning | Public headers rely on transitive includes for several Maya types. | `source/smoothWeightsTool.h:14-49`, `source/transferWeightsTool.h:14-49`. | Add direct includes for `MColor`, array types, `MFnDagNode`, `MFnDependencyNode`, and `MPlug`; add `<cmath>`/`<cstdio>` where used. |
| Warning | TBB is included through public tool headers even though the parallel implementation is private to the `.cpp` files. | Both headers include `<tbb/parallel_for.h>` and `<tbb/blocked_range.h>`. | Move TBB includes into the `.cpp` files and link the Maya 2026-bundled oneTBB 2021.12 (`tbb12.lib`). |
| Blocker for correct registration | `registerContextCommand` is called without the tool-command syntax callback although both tool classes define `newSyntax()`. | `source/pluginMain.cpp:29-39`; `source/smoothWeightsTool.cpp:134-163`; `source/transferWeightsTool.cpp:131-159`. | Pass `smoothWeightsTool::newSyntax` and `transferWeightsTool::newSyntax` as the fifth registration argument. |
| Warning | Registration overwrites the first status with the second and does not roll back a partial registration. Deregistration is not in reverse order. | `source/pluginMain.cpp:24-61`. | Accumulate failures, roll back the first context if the second registration fails, and deregister transfer before smooth. |
| Verified valid | `MFnSkinCluster` all-influence `getWeights` and array `setWeights` overloads remain available. | `source/smoothWeightsTool.cpp:320,381,1490,2038`; `source/transferWeightsTool.cpp:311,372,1473,2023`. | Keep the existing weight algorithms. Add status checks only where needed for robust error reporting. |
| Verified valid | Legacy and Viewport 2 `MPxContext` event overloads used here remain available. | Both context classes and their `doPress`/`doDrag`/`doRelease` overloads. | No context API rewrite required. |
| Verified valid | `MItMeshVertex`, `MItMeshEdge`, `MItMeshPolygon`, `MItDependencyGraph`, and `MMeshIntersector::create` calls used here remain compatible. | Both tool implementations. | No geometry-iterator migration required. |
| Pre-existing defect | TBB workers call Maya APIs and update shared weight state concurrently. Component creation and topology queries occur inside parallel work; sibling tasks can read/write `currentWeights`. | `source/smoothWeightsTool.cpp:1989-2034,2080-2125,2187-2188,2362-2366`; `source/transferWeightsTool.cpp:1976-2020,2064-2075`. | Do not redesign the numerical algorithm during this compatibility port. Record for follow-up and runtime stress testing; a future fix should precompute topology and double-buffer numeric weights. |
| Pre-existing defect | Transfer source/destination defaults are `-1` but are cast to unsigned indices before validation. | `source/transferWeightsTool.cpp:40,50,2121-2128`. | Follow-up validation fix; test locked and unset influences before changing array access. |
| Pre-existing defect | Multi-mesh selections can contribute component indices that do not belong to the active mesh. | `source/smoothWeightsTool.cpp:905-907,1373-1414`; `source/transferWeightsTool.cpp:883-885,1356-1397`. | Follow-up fix: ignore selection entries whose DAG path does not match `meshDag`. |
| Pre-existing defect | Boundary/opposite-face paths do not consistently check iterator/intersector status or prove that an opposite element was found. | `source/smoothWeightsTool.cpp:2309,3038-3069,3115-3119`; `source/transferWeightsTool.cpp:2187,2779-2825,2871-2875`. | Follow-up robustness fix with negative-index guards and failure returns. |
| Pre-existing defect | Brush size can be zero while falloff calculations divide by size. | `source/smoothWeightsTool.cpp:1057,1825,2126`; `source/transferWeightsTool.cpp:1038,1814,2075`. | Follow-up no-op/validation fix after golden-path comparisons. |
| Pre-existing anomaly | Transfer zeroes a full influence row but writes only source/destination values, so normalization cannot restore other influences. | `source/transferWeightsTool.cpp:1970,2135-2157`. | Do not silently alter during the port. Compare against an upstream reference scene before deciding whether this is intentional. |

No removed Maya 2026 API was confirmed by the syntax-only compile. The absence of compiler errors does not prove ABI compatibility, runtime safety, or identical behavior.

## 6. Registration and loading workflow

The existing workflow is:

1. The installer writes `brSmoothWeights.mod` into a Maya module directory.
2. `userSetup.py` defers a Skin-menu hook outside batch mode.
3. Opening the Skin menu lazily calls `loadPlugin brSmoothWeights`.
4. The menu exposes **Paint Smooth Weights Tool** and **Paint Transfer Weights Tool**.
5. Each MEL launcher creates the corresponding native context and selects it with `setToolTo`.

This workflow should be preserved. The module template currently stops at Maya 2025 and must gain a Windows x64 Maya 2026 entry pointing to `plug-ins/win64/2026`.

## 7. External dependencies

### Required

- Maya 2026 C++ SDK/DevKit headers and import libraries.
- Microsoft Visual C++ build tools matching Autodesk's Maya 2026 requirement.
- oneTBB headers and `tbb12.lib` shipped with Maya 2026.
- Maya's MEL runtime and existing UI/resource scripts.

### Not required by the native source

- Qt
- Python SDK
- FBX SDK
- OpenGL
- Boost
- Paid third-party libraries

No new paid dependency is needed.

## 8. Build-system gaps and proposed CMake design

The port adds a root `CMakeLists.txt` with these constraints:

- CMake 3.27.3 or newer.
- Windows x64 and MSVC only for this target.
- Explicit `MAYA_LOCATION` cache input with a Maya 2026 default.
- Validate required Maya headers and libraries under that root.
- C++17, `/EHsc`, and the dynamic MSVC runtime (`/MD`) to match Maya.
- Define `NT_PLUGIN` and request the unmangled `initializePlugin`/`uninitializePlugin` linker aliases used by the upstream Windows project.
- Link `Foundation`, `OpenMaya`, `OpenMayaUI`, `OpenMayaAnim`, `OpenMayaRender`, and `tbb12`.
- Produce `brSmoothWeights.mll`.
- Install into `modules/brSmoothWeights/plug-ins/win64/2026` under a chosen prefix.

The archived `source/env/versions/1.0.0/*` files will be preserved but not used as the maintained build system.

## 9. GitHub Actions strategy

Autodesk Platform Services publishes official Maya 2026 Windows DevKit links, including Update 3. The link verified for this audit is:

`https://autodesk-adn-transfer.s3.us-west-2.amazonaws.com/ADN+Extranet/M%26E/Maya/devkit+2026/Autodesk_Maya_2026_3_Update_DEVKIT_Windows.zip`

The package returned HTTP 200, `Content-Type: application/zip`, and `Content-Length: 552487216` on 2026-11-23. It is an Autodesk ADN-hosted package reached from Autodesk's official Maya API page.

The workflow:

1. Runs on `windows-2022`.
2. Verifies Visual Studio 2022 17.8.3+ with x64 C++ tools.
3. Downloads the pinned official DevKit to the runner temporary directory.
4. Extracts it only on the ephemeral runner.
5. Locates the SDK root from `include/maya/MFnPlugin.h` and validates the required libraries.
6. Configures with the Visual Studio 17 2022 generator and x64 architecture.
7. Builds Release.
8. Verifies the `.mll` exists, is x64, and exports both plug-in entry points.
9. Uploads only the compiled plug-in as a workflow artifact.

No Autodesk SDK files or credentials will be committed. The SDK archive will not be uploaded as an artifact. If the official URL becomes unavailable, the maintainer can update `MAYA_DEVKIT_URL` in the workflow to another authorized package or use a Windows self-hosted runner with a locally installed SDK.

## 10. Installation and script findings

- Add a Maya 2026 Windows x64 module stanza to `resources/module_template.mod`.
- Build/install the binary at `modules/brSmoothWeights/plug-ins/win64/2026/brSmoothWeights.mll`.
- Preserve the original installer-generated module workflow.
- The installer derives `MODULE_NAME` from the distribution folder name, so the packaged root must remain named `brSmoothWeights`.
- `dragDropInstaller.py` initially read the EULA as bytes and passed it to `cmds.scrollField`, which is incompatible with Python 3 text expectations. The port reads it as UTF-8 text before display.
- The uninstall parser uses `line.split(" ")[-1]`, which is fragile for Windows paths containing spaces. This is an installer robustness issue, not a plug-in loading blocker.
- `userSetup.py` contains no Python-2-only syntax and needs no migration.
- MEL UI internals, context lifecycle, SVG rendering, influence menus, and in-view messages require Maya 2026 runtime testing.

## 11. Proposed implementation stages

1. Import the unchanged upstream and add this audit.
2. Apply minimal native compatibility/registration fixes and add direct includes without changing numerical algorithms.
3. Add CMake and the GitHub Actions workflow.
4. Add the Maya 2026 module entry, installer text fix, README build/install instructions, and testing checklist.
5. Run all locally available static checks; clearly mark link/runtime checks that require the official VS2022 environment or Maya 2026.

## 12. Modification record

| Stage | Files | Status |
| --- | --- | --- |
| Baseline import | All tracked upstream files | Imported unchanged from `bb017e67c2bf7ca03cb626cacfa2ca58b3a66bd8`. |
| Audit | `MAYA2026_PORTING_AUDIT.md` | Added before implementation changes. |
| Native compatibility | `source/pluginMain.cpp`, `source/smoothWeightsTool.h`, `source/smoothWeightsTool.cpp`, `source/transferWeightsTool.h`, `source/transferWeightsTool.cpp` | Added direct includes, moved private TBB includes, replaced deprecated plug reads, preserved failed-read defaults, registered tool syntax callbacks, added registration rollback and reverse-order deregistration. Numerical algorithms unchanged. |
| Build system | `CMakeLists.txt` | Added a Windows x64 MSVC target for `brSmoothWeights.mll`, C++17, dynamic MSVC runtime, Maya 2026 SDK discovery, bundled oneTBB linkage, module-layout install rules, and the upstream unmangled plug-in entry-point export aliases. |
| CI and binary verification | `.github/workflows/build-maya2026-windows.yml`, `tests/verify_mll.py` | Added a `windows-2022` workflow that verifies VS2022/CMake versions, downloads the pinned official Autodesk DevKit ephemerally, builds and installs the module-layout binary, verifies AMD64 and both plug-in exports, uploads only the `.mll`, and always removes the downloaded SDK. |
| Packaging and documentation | `resources/module_template.mod`, `dragDropInstaller.py`, `README.md`, `versions.md`, `MAYA2026_INSTALLATION.md`, `MAYA2026_TESTING_CHECKLIST.md` | Added the Maya 2026 Windows module block, UTF-8 EULA decoding for Python 3, build/install/launch instructions, an explicit tested/unverified checklist, and preserved credits/license references. |

## 13. Validation status

| Check | Status |
| --- | --- |
| Upstream repository inventory | Completed. |
| Maya 2026 header/signature inspection | Completed against installed headers. |
| Unchanged-source syntax compilation | Passed with MSVC 19.51; not the official VS2022 toolchain. |
| Ported-source syntax compilation | Passed for all three translation units with MSVC 19.51 and Maya 2026 headers; link not attempted. |
| Unchanged-source link | Blocked locally by missing `msvcprt.lib` in the incomplete VS2026 Build Tools installation. |
| CMake configure | Passed with CMake 4.4.5, NMake, and MSVC 19.51 using static-library compiler probes; all Maya 2026 headers/libraries were found. Normal compiler probes cannot link locally because the CRT import libraries are missing. |
| CMake compile | All three translation units compiled successfully; no `.mll` was produced. |
| CMake link | Blocked locally by missing `msvcprt.lib` in the incomplete VS2026 Build Tools installation. |
| Workflow YAML and PowerShell parse | Passed locally for the workflow and all five PowerShell script blocks; the hosted workflow subsequently executed successfully. |
| PE verifier | Passed against the upstream Maya 2025 x64 `.mll`, correctly rejected a non-PE file, and independently passed on the hosted Maya 2026 artifact. |
| Installer Python syntax | Passed locally with Python 3.14; Maya installer UI execution is not tested. |
| Module template and documentation links | Passed static checks; Maya module discovery and lazy Skin-menu loading are not tested. |
| Core algorithm comparison | Passed: `performSmooth`, `computeWeights`, smoothing falloff, `performTransfer`, `computeTransfer`, and transfer falloff are byte-for-byte unchanged from upstream. |
| Official DevKit endpoint | Verified HTTP 200 with `Content-Length: 552487216` for the pinned Autodesk archive. |
| Final clean CMake configure | Passed with CMake 4.4.5, NMake, and MSVC 19.51 using static-library compiler probes; all required SDK components were found. |
| CMake entry-point export configuration | Passed with CMake 4.4.5, Ninja, and MSVC 19.51; generated link flags include `/export:initializePlugin` and `/export:uninitializePlugin`. |
| GitHub Actions build | Passed: [run 45275333759](https://github.com/254odari/brSmoothWeights-Maya2026/actions/runs/45275333759) at commit `228227f` built and installed the `.mll` with VS2022 and the official DevKit. |
| Hosted artifact contents | Passed: the artifact contains only `brSmoothWeights.mll` (143,360 bytes; SHA-256 `f5b2494d3666f80342b2f1839fd9badb12eaaf484b2a7a403b233607e555447d`). |
| Maya 2026 headless load/unload/reload | Passed in isolated Autodesk Maya 2026.2 `mayapy`: the artifact loaded from the reported path, both tool commands returned valid syntax, and unload/reload/unload succeeded. |
| Smoothing/transfer numerical, UI, and stress behavior | Not tested; requires interactive Maya 2026 testing. |

The first hosted run, [45272798770](https://github.com/254odari/brSmoothWeights-Maya2026/actions/runs/45272798770), compiled successfully but failed PE verification because the CMake target omitted the upstream Windows entry-point export aliases. Commit `228227f` restored those linker options, and the rerun passed. The original `leightonayange` destination was not writable by the authenticated account, so the verified repository was published under `254odari`.

## 14. Authoritative references

- [Autodesk Maya API / SDK downloads](https://aps.autodesk.com/developer/overview/maya-api)
- [Autodesk Maya 2026 Developer Help](https://help.autodesk.com/view/MAYADEV/2026/ENU/)
- [Autodesk Maya 2026 API Update Guide](https://blog.autodesk.io/maya-2026-api-update-guide/)
- [Maya 2026 MFnMesh reference](https://help.autodesk.com/cloudhelp/2026/ENU/MAYA-API-REF/cpp_ref/class_m_fn_mesh.html)
- [Maya 2026 MFnSkinCluster reference](https://help.autodesk.com/cloudhelp/2026/ENU/MAYA-API-REF/cpp_ref/class_m_fn_skin_cluster.html)
- [Maya 2026 MItMeshVertex reference](https://help.autodesk.com/cloudhelp/2026/ENU/MAYA-API-REF/cpp_ref/class_m_it_mesh_vertex.html)
- [Maya 2026 MPxContext reference](https://help.autodesk.com/cloudhelp/2026/ENU/MAYA-API-REF/cpp_ref/class_m_px_context.html)
- [Maya 2026 MFnPlugin reference](https://help.autodesk.com/cloudhelp/2026/ENU/MAYA-API-REF/cpp_ref/class_m_fn_plugin.html)
- [Maya 2026 MPlug reference](https://help.autodesk.com/cloudhelp/2026/ENU/MAYA-API-REF/cpp_ref/class_m_plug.html)
