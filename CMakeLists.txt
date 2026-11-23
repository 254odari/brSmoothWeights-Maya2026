cmake_minimum_required(VERSION 3.27.3)

project(brSmoothWeights VERSION 1.2.0 LANGUAGES CXX)

if(NOT WIN32)
    message(FATAL_ERROR "This port targets Autodesk Maya 2026 on Windows 64-bit.")
endif()

if(NOT MSVC)
    message(FATAL_ERROR "Autodesk Maya 2026 Windows plug-ins require the Microsoft C++ toolchain.")
endif()

if(MSVC_VERSION LESS 1938)
    message(FATAL_ERROR "Maya 2026 requires Visual Studio 2022 version 17.8 or newer.")
endif()

set(MAYA_LOCATION "C:/Program Files/Autodesk/Maya2026" CACHE PATH
    "Autodesk Maya 2026 installation containing include and lib")

find_path(MAYA_INCLUDE_DIR
    NAMES maya/MFnPlugin.h
    PATHS "${MAYA_LOCATION}/include"
    NO_DEFAULT_PATH
    REQUIRED
)

find_path(MAYA_TBB_INCLUDE_DIR
    NAMES tbb/parallel_for.h
    HINTS "${MAYA_LOCATION}/include/oneapi"
    NO_DEFAULT_PATH
    REQUIRED
)

find_library(MAYA_FOUNDATION_LIBRARY
    NAMES Foundation.lib
    PATHS "${MAYA_LOCATION}/lib"
    NO_DEFAULT_PATH
    REQUIRED
)
find_library(MAYA_OPENMAYA_LIBRARY
    NAMES OpenMaya.lib
    PATHS "${MAYA_LOCATION}/lib"
    NO_DEFAULT_PATH
    REQUIRED
)
find_library(MAYA_OPENMAYAUI_LIBRARY
    NAMES OpenMayaUI.lib
    PATHS "${MAYA_LOCATION}/lib"
    NO_DEFAULT_PATH
    REQUIRED
)
find_library(MAYA_OPENMAYAANIM_LIBRARY
    NAMES OpenMayaAnim.lib
    PATHS "${MAYA_LOCATION}/lib"
    NO_DEFAULT_PATH
    REQUIRED
)
find_library(MAYA_OPENMAYARENDER_LIBRARY
    NAMES OpenMayaRender.lib
    PATHS "${MAYA_LOCATION}/lib"
    NO_DEFAULT_PATH
    REQUIRED
)
find_library(MAYA_TBB_LIBRARY
    NAMES tbb12.lib
    PATHS "${MAYA_LOCATION}/lib"
    NO_DEFAULT_PATH
    REQUIRED
)

set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreadedDLL")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_library(brSmoothWeights SHARED
    source/pluginMain.cpp
    source/smoothWeightsTool.cpp
    source/smoothWeightsTool.h
    source/transferWeightsTool.cpp
    source/transferWeightsTool.h
)

target_include_directories(brSmoothWeights PRIVATE
    "${CMAKE_CURRENT_SOURCE_DIR}/source"
    "${MAYA_INCLUDE_DIR}"
    "${MAYA_TBB_INCLUDE_DIR}"
)

target_compile_definitions(brSmoothWeights PRIVATE
    NT_PLUGIN
    _CRT_SECURE_NO_WARNINGS
)

target_compile_options(brSmoothWeights PRIVATE
    /W3
    /permissive-
    /EHsc
)

target_link_libraries(brSmoothWeights PRIVATE
    "${MAYA_FOUNDATION_LIBRARY}"
    "${MAYA_OPENMAYA_LIBRARY}"
    "${MAYA_OPENMAYAUI_LIBRARY}"
    "${MAYA_OPENMAYAANIM_LIBRARY}"
    "${MAYA_OPENMAYARENDER_LIBRARY}"
    "${MAYA_TBB_LIBRARY}"
)

set_target_properties(brSmoothWeights PROPERTIES
    OUTPUT_NAME brSmoothWeights
    PREFIX ""
    SUFFIX ".mll"
)

install(TARGETS brSmoothWeights
    RUNTIME DESTINATION plug-ins/win64/2026
)
