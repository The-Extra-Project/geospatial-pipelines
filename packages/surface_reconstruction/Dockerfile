FROM --platform=x86_64 ubuntu:22.04 as build

ARG UBUNTU_FRONTEND=noninteractive
## installing libcgal and dependencies 
RUN apt-get update &&  apt-get install -y cmake build-essential libeigen3-dev libpng-dev libjpeg-dev libcgal-dev g++ coreutils --assume-yes

## setting up the build enviornment and build files: 
RUN mkdir -p /usr/src/app/reconstruction


COPY ./CMakeLists.txt /usr/src/app/reconstruction/CMakeLists.txt

ADD ./ /usr/src/app/reconstruction/

WORKDIR /usr/src/app/reconstruction


COPY ./lib/  ./lib/  
COPY ./CMakeLists.txt ./CMakeLists.txt
COPY ./FindLAS.cmake ./FindLAS.cmake
COPY  . .
RUN realpath --relative-to="FindLAS.cmake" "CMakeLists.txt" 

##  building the lastools:

RUN mkdir -p  ./lib/LAStools/build/ \
    && cd ./lib/LAStools/build \
    && cmake ../ -DCMAKE_BUILD_TYPE=Release \
    && make

RUN mkdir -p ./build \
    && cd ./build \
    && cmake ../ -DCMAKE_BUILD_TYPE=Release \
    && make 

COPY  . .
RUN chmod +x run_surface_reconstruction.sh

FROM --platform=x86_64 build as run

COPY --from=build /usr/src/app/reconstruction /usr/src/app/reconstruction

ENTRYPOINT [ "./run_surface_reconstruction.sh" ]