
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.0 as base

WORKDIR /usr/src/app/georender

LABEL org.opencontainers.image.description="Pipeline pointcloud / geospatial data cropping" \
      org.opencontainers.image.authors="Dhruv Malik" \
      org.opencontainers.image.version="0.1"


RUN apt-get update && apt-get install -y git wget jq p7zip-full python3.10-venv --assume-yes python3 python3-pip  --assume-yes  

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

RUN python3 -m venv /opt/venv

COPY requirements.txt requirements.txt 

## installing PDAL in order to then use their bindings 

WORKDIR /

RUN apt install -y cmake git mlocate

## getting the geotiff for the setup of the pdal 

ENV DGEOTIFF_LIBRARY='$(locate geotiff.h)'
ENV DGEOTIFF_INCLUDE_DIR=/usr/include/geotiff
RUN wget https://github.com/PDAL/PDAL/releases/download/2.6.0/PDAL-2.6.0-src.tar.bz2 && \
7z x PDAL-2.6.0-src.tar.bz2 && 7z x PDAL-2.6.0-src.tar && rm -rf PDAL-2.6.0-src.tar.bz2  &&\
cd PDAL-2.6.0-src && mkdir build && cd build && cmake .. 

RUN  pip install -r requirements.txt

COPY . .

FROM base as run 

ENV DISPLAY "0.0"

COPY --chmod=777 --from=base  /usr/src/app/georender/ /usr/src/app/georender/

WORKDIR /usr/src/app/georender

EXPOSE 8081
