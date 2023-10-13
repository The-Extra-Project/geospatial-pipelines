
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.7.2 as base

WORKDIR /usr/src/app/georender

LABEL org.opencontainers.image.description="Pipeline 3D surface reconstruction" \
      org.opencontainers.image.authors="Dhruv Malik" \
      org.opencontainers.image.version="0.1"


RUN apt-get update && apt-get install -y git wget jq p7zip-full python3.10-venv --assume-yes python3 python3-pip  --assume-yes  

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

RUN python3 -m venv /opt/venv

COPY requirements.txt requirements.txt 

RUN  pip install -r requirements.txt

COPY . .

FROM base as run


COPY --chmod=777 --from=base  /usr/src/app/georender/ /usr/src/app/georender/

WORKDIR /usr/src/app/georender

EXPOSE 8081


RUN chmod +x ./src/georender.py && chmod +x run_georender_test.sh

ENTRYPOINT [ "./run_module.sh" ]     