FROM --platform=x86_64 ubuntu:22.04 as build

ARG UBUNTU_FRONTEND=noninteractive

## installing libcgal and dependencies 
RUN apt-get update &&  apt-get install -y cmake build-essential libeigen3-dev libpng-dev libjpeg-dev libcgal-dev g++ --assume-yes

## setting up the build enviornment and build files: 

RUN mkdir -p /usr/src/app/reconstruction




WORKDIR /usr/src/app

COPY ./CMakeLists.txt /usr/src/app/reconstruction/CMakeLists.txt
COPY ./FindLAS.cmake /usr/src/app/reconstruction/FindLAS.cmake
COPY ./src/ /usr/src/app/reconstruction/src/
COPY ./lib/LAStools /usr/src/app/reconstruction/lib/LAStools
##  building the lastools:

RUN mkdir -p  /usr/src/app/reconstruction/lib/LAStools/build/ \
    && cd /usr/src/app/reconstruction/lib/LAStools/build \
    && cmake ../ -DCMAKE_BUILD_TYPE=Release \
    && make

RUN mkdir -p /usr/src/app/reconstruction/build \
    && cd /usr/src/app/reconstruction/build \
    && cmake ../ -DCMAKE_BUILD_TYPE=Release \
    && make 

FROM --platform=x86_64 build as run

COPY --from=build /usr/src/app/reconstruction /usr/src/app/reconstruction

ENTRYPOINT [ "./reconstruction/run_surface_reconstruction.sh" ]