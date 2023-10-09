cmake_minimum_required(VERSION 3.1...4.15)
add_definitions(-Wno-dev)
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Debug)
set(Boost_USE_STATIC_LIBS OFF) 
set(Boost_USE_MULTITHREADED ON)  
set(Boost_USE_STATIC_RUNTIME OFF) 

## PoissonRecon
set(DEFAULT_FEM_DEGREE, 1)
set(DEFAULT_FEM_BOUNDARY, "Neumann" )

project( pipeline_pointcloud )



# Find includes in corresponding build directories
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(LAS_LIBRARIES "./lib/LAStools" )
set(CGAL_DATA_DIR ".")

# CGAL and its components
find_package( CGAL QUIET COMPONENTS  )

include(${CGAL_USE_FILE})

if ( NOT CGAL_FOUND )
  message(STATUS "This project requires the CGAL library, and will not be compiled.")
  return()  
endif()

install()

set(libjpeg_DIR, "/usr/include/libjpeg")
list(APPEND CMAKE_PREFIX_PATH ${libjpeg_DIR})


include(${CMAKE_CURRENT_SOURCE_DIR}/FindlibJPEG.cmake)

#find_package(libJPEG)
#target_link_libraries(surface_reconstruction libJPEG )
#target_link_libraries( poisson_recon libJPEG)

message(STATUS "CGAL_FOUND : ${CGAL_FOUND}")
message(STATUS "CGAL_LIBRARIES : ${CGAL_LIBRARIES}")
message(STATUS "CGAL_INCLUDE_DIRS : ${CGAL_INCLUDE_DIRS}")
# message(STATUS "CGAL_3RD_PARTY_LIBS : ${CGAL_3RD_PARTY_LIBRARIES}")
# message(STATUS "LIBJPEG : ${JPEG_VERSION}")


# Boost and its components
find_package( Boost REQUIRED )

if ( NOT Boost_FOUND )
  message(STATUS "This project requires the Boost library, and will not be compiled.")
  return()  
endif()

find_package(Eigen3 3.1.0 QUIET)
include(CGAL_Eigen3_support)


set(surface_reconstruction_SOURCE_DIR "." )


#add_subdirectory(${surface_reconstruction_SOURCE_DIR}/lib/PoissonRecon/)

message(STATUS "laslib : ${LAS_LIBRARIES}")
message("CGAL version: ${CGAL_VERSION}")
message("surface_reconstruction_SOURCE_DIR: ${surface_reconstruction_SOURCE_DIR}")
include(${CMAKE_CURRENT_SOURCE_DIR}/FindLAS.cmake)

# include for local directory
include_directories(${surface_reconstruction_SOURCE_DIR}/lib/LAStools/)
include_directories(${surface_reconstruction_SOURCE_DIR}/lib/LAStools/LASlib/inc/)
include_directories(${surface_reconstruction_SOURCE_DIR}/lib/LAStools/LASzip/src/)
include_directories(${surface_reconstruction_SOURCE_DIR}/build/)



if(TARGET CGAL::Eigen3_support)

# ############################
create_single_source_cgal_program("normal_and_reconstruction.cpp")

add_executable( normal_and_reconstruction  ${surface_reconstruction_SOURCE_DIR}/src/normal_and_reconstruction.cpp)
target_link_libraries(normal_and_reconstruction ${Boost_LIBRARIES})
target_link_libraries(normal_and_reconstruction CGAL::CGAL ${CGAL_LIBRARIES})
target_link_libraries(normal_and_reconstruction CGAL::CGAL ${LAS_LIBRARIES})
#target_link_libraries(normal_and_reconstruction CGAL::CGAL ${Eigen3_LIBRARIES})
#target_link_libraries(normal_and_reconstruction PUBLIC CGAL::Eigen3_support)


else()
  message("NOTICE: The examples require Eigen 3.1 (or greater) will not be compiled.")
endif()