cmake_minimum_required(VERSION 3.1...3.15)

project( surface_reconstruction )

set(main_SOURCE_DIR ".")
set(LAS_LIBRARIES "./lib/LAStools" )
set(CGAL_DATA_DIR "./datas" )
# CGAL and its components
find_package( CGAL QUIET COMPONENTS  )
find_package (Eigen3)



if ( NOT CGAL_FOUND )
  message(STATUS "This project requires the CGAL library, and will not be compiled.")
  return()  
endif()

INCLUDE(${PROJECT_SOURCE_DIR}/FindLAS.cmake)


message(STATUS "CGAL_FOUND : ${CGAL_FOUND}")
message(STATUS "CGAL_LIBRARIES : ${CGAL_LIBRARIES}")
message(STATUS "CGAL_INCLUDE_DIRS : ${CGAL_INCLUDE_DIRS}")

# Boost and its components
find_package( Boost REQUIRED )

if ( NOT Boost_FOUND )
  message(STATUS "This project requires the Boost library, and will not be compiled.")
  return()  
endif()

message(STATUS "laslib : ${LAS_LIBRARIES}")

# include for local directory
include_directories(${main_SOURCE_DIR}/lib/LAStools/LASlib/inc/)
include_directories(${main_SOURCE_DIR}/lib/LAStools/LASzip/src/)
include_directories(${main_SOURCE_DIR}/usr/src/app/lib/)
include_directories(/usr/include/eigen3/)
include(${CGAL_USE_FILE})

# Creating entries for target: main
# ############################

add_executable( normal_and_reconstruction  ${PROJECT_SOURCE_DIR}/src/normal_and_reconstruction.cpp)
target_link_libraries(normal_and_reconstruction CGAL::CGAL ${LAS_LIBRARIES})

add_to_cached_list( CGAL_EXECUTABLE_TARGETS compute_normals )