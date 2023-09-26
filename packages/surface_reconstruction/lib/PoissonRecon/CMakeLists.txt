cmake_minimum_required(VERSION 3.1...4.15)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_BUILD_TYPE Debug)


## PoissonRecon
set(DEFAULT_FEM_DEGREE, 1)
set(DEFAULT_FEM_BOUNDARY, "Neumann" )

project( poisson_recon )

# Find includes in corresponding build directories
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(POISSON_RECON_LIBRARIES "./lib/PoissonRecon")


include_directories(${poisson__SOURCE_DIR}/bin/Linux)
include_directories(${poisson__SOURCE_DIR}/src)
include_directories(${poisson__SOURCE_DIR})
include_directories(/tmp/boost)
include_directories(/tmp/libjpeg)

find_package(Boost REQUIRED)
message("BOOST_DIR", ${BOOST_ROOT})

find_package(libJPEG )

add_executable(PoissonRecon ${poisson__SOURCE_DIR}/Src/PoissonRecon.cpp)

add_dependencies(Image.h )
add_executable(PoissonRecon)

target_link_libraries(PoissonRecon ${Boost_LIBRARIES})