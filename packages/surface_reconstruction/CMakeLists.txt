cmake_minimum_required(VERSION 3.1...4.15)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


project( main )


# Find includes in corresponding build directories
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(LAS_LIBRARIES "./lib/LAStools" )
set(CGAL_DATA_DIR ".")
set(EIGEN_dir "/usr/include/eigen3/")
# CGAL and its components
find_package( CGAL QUIET COMPONENTS  )
find_package (Eigen3)
include(${CGAL_USE_FILE})

if ( NOT CGAL_FOUND )
  message(STATUS "This project requires the CGAL library, and will not be compiled.")
  return()  
endif()

message(STATUS "CGAL_FOUND : ${CGAL_FOUND}")
message(STATUS "CGAL_LIBRARIES : ${CGAL_LIBRARIES}")
message(STATUS "CGAL_INCLUDE_DIRS : ${CGAL_INCLUDE_DIRS}")
message(STATUS "CGAL_3RD_PARTY_LIBS : ${CGAL_3RD_PARTY_LIBRARIES}")

# Boost and its components
find_package( Boost REQUIRED )

if ( NOT Boost_FOUND )
  message(STATUS "This project requires the Boost library, and will not be compiled.")
  return()  
endif()

# Eigen
find_package(Eigen3)
include( ${EIGEN3_USE_FILE} )  

message(STATUS "laslib : ${LAS_LIBRARIES}")
include(${CMAKE_CURRENT_SOURCE_DIR}/FindLAS.cmake)
# include for local directory
include_directories(${main_SOURCE_DIR}/lib/LAStools/LASlib/inc/)
include_directories(${main_SOURCE_DIR}/lib/LAStools/LASzip/src/)
include_directories(${main_SOURCE_DIR}/usr/src/app/lib/)

include_directories(${CGAL_INCLUDE_DIRS}/eigen3/)

find_package(Eigen3 REQUIRED)

link_directories(${Eigen3_INCLUDE_DIRS})

# Creating entries for target: NORMAL_AND
# ############################
add_executable( normal_and_reconstruction  ${main_SOURCE_DIR}/src/normal_and_reconstruction.cpp)
target_link_libraries(normal_and_reconstruction CGAL::CGAL ${CGAL_LIBRARIES})
target_link_libraries(normal_and_reconstruction CGAL::CGAL ${LAS_LIBRARIES})
target_link_libraries(normal_and_reconstruction CGAL::CGAL ${Eigen3_LIBRARIES})