FROM --platform= pdal/pdal as base

LABEL org.opencontainers.image.description="Pipeline 3D surface reconstruction" \
      org.opencontainers.image.authors="Dhruv Malik" \
      org.opencontainers.image.version="0.1"


ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

WORKDIR /
FROM --platform=x86_64 base as build

RUN mkdir -p /usr/src/app/georender


COPY requirements.txt /usr/src/app/georender/requirements.txt 

COPY . /usr/src/app/georender/

RUN apt-get update && apt-get install -y git wget jq p7zip-full --assume-yes python3 python3-pip  --assume-yes  


RUN cd /usr/src/app/georender/ &&  pip install -r requirements.txt


FROM --platform=x86_64 build as run

COPY --from=builder /usr/src/app/georender /usr/src/app/georender

WORKDIR /usr/src/app/georender

#RUN nohup python watcher.py &

## also either running the below command in order to have watch mode (or setting up the nohup script )

RUN watchmedo log \
    --patterns="*.py;*.txt" \
    --ignore-directories \
    --recursive \
    --verbose  .




RUN chmod 777 ./run_module.sh 

EXPOSE 8081
ENTRYPOINT [  "./run_module.sh" ]   