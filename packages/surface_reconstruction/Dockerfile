FROM --platform=x86_64 ubuntu:22.04 as build

ARG UBUNTU_FRONTEND=noninteractive
## installing libcgal and depdendencies of poissonRecon
RUN apt-get update &&  apt-get install -y cmake build-essential libeigen3-dev libpng-dev libjpeg-dev libcgal-dev g++ coreutils \
 xz-utils \
 curl \
 git \
 gcc \
 make \
 g++ \
 wget \
 libjpeg-dev \
 libjpeg-turbo8-dev  --assume-yes \
 && rm -rf /var/lib/apt/lists/*

#
## installation of boost (very time taking process, need to find the alternative)
RUN wget https://boostorg.jfrog.io/artifactory/main/release/1.83.0/source/boost_1_83_0.tar.bz2 && \
 tar  -xf boost_1_83_0.tar.bz2 && \
 cd boost_1_83_0 && \
 ./bootstrap.sh --prefix=/usr/ && \
./b2 install && \
rm -rf /tmp/*


# RUN git clone https://github.com/mkazhdan/PoissonRecon.git  \
# && cd PoissonRecon/ \
#   && mkdir build \
#   && make -j8 \
#   && make install \
   


## setting up the build enviornment and build files: 
RUN mkdir -p /usr/src/app/reconstruction

WORKDIR /


COPY ./lib/  ./usr/src/app/reconstruction/lib/  
COPY ./CMakeLists.txt ./usr/src/app/reconstruction/CMakeLists.txt
COPY ./FindLAS.cmake ./usr/src/app/reconstruction/FindLAS.cmake
COPY ./ ./usr/src/app/reconstruction/
ADD --chown=user:777  ./src/ ./usr/src/app/reconstruction/src/
##  building the lastools:

RUN mkdir -p  /usr/src/app/reconstruction/lib/LAStools/build/ \
    && cd /usr/src/app/reconstruction/lib/LAStools/build \
    && cmake ../ -DCMAKE_BUILD_TYPE=Release \
    && make

RUN mkdir -p /usr/src/app/reconstruction/build \
    && cd /usr/src/app/reconstruction/build \
    && cmake ../ -DCMAKE_BUILD_TYPE=Release \
    && make 

COPY  run_surface_reconstruction.sh ./

RUN chmod +x run_surface_reconstruction.sh

FROM --platform=x86_64 build as run

COPY --from=build /usr/src/app/reconstruction /usr/src/app/reconstruction

ENTRYPOINT [ "./run_surface_reconstruction.sh" ]