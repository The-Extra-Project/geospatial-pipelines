FROM --platform=arm64 ubuntu22.04:latest as build

RUN apt-get update && apt install -y python3-dev 

WORKDIR /app
COPY .  /e2e/

ENTRYPOINT [ "./run.sh" ]
