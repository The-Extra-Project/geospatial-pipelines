FROM --platform=x86_64 pdal/pdal as base

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /

FROM --platform=x86_64 base as builder

RUN mkdir -p /usr/src/app/georender

ENV ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 

RUN apt-get update && apt-get install -y git wget jq p7zip-full --assume-yes python3-pip  --assume-yes  python3-dev


RUN cd /usr/src/app/georender/ &&  pip3 install -r requirements.txt

COPY . /usr/src/app/georender/


FROM --platform=x86_64 builder as run

COPY --from=builder /usr/src/app/georender /usr/src/app/georender

WORKDIR /usr/src/app/georender


RUN chmod 777 ./run_module.sh 

EXPOSE 8081
ENTRYPOINT [  "./run_module.sh" ]   