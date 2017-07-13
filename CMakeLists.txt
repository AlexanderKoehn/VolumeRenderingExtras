cmake_minimum_required(VERSION 2.8.9)

project(VolumeRenderingExtras)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/VolumeRenderingExtras")
set(EXTENSION_CATEGORY "Visualization")
set(EXTENSION_CONTRIBUTORS "Anna Fruehstueck (BWH), Steve Pieper (Isomics, Inc.), Alexander Koehn (Fraunhofer MEVIS)")
set(EXTENSION_DESCRIPTION "Improvements for the Volume Rendering Module")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/VolumeRenderingExtras.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/VolumeRenderingExtras/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(TransferFunctionEditor)
add_subdirectory(ExposureRenderLink)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
