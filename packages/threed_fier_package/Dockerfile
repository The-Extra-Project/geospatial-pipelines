FROM  ubuntu:22.04 as build

ENV DEBIAN_FRONTEND noninteractive

RUN  apt-get update && \
    apt-get install -y  software-properties-common && \
    add-apt-repository ppa:ubuntugis/ubuntugis-unstable && \
    apt-get install -y libcgal-dev libboost-all-dev libyaml-cpp-dev libgdal-dev unzip cmake git gcc g++ build-essential python3-pip


WORKDIR /

## installing the LASTools
RUN git clone https://github.com/LAStools/LAStools.git && \
cd LAStools && cmake -DCMAKE_BUILD_TYPE=Release .  &&  make install && make install

## and finally building the threeD_fier
RUN git clone https://github.com/tudelft3d/3dfier.git &&  cd 3dfier; mkdir build; cd build; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/usr/local/laslib ../

WORKDIR /usr/app/citygml/

COPY . .

#COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

FROM build as run

WORKDIR /usr/app/citygml

COPY --from=build /usr/app/citygml /usr/app/citygml 

RUN chmod  +x run_threedfier.sh

ENTRYPOINT [ "./run_threedfier.sh" ] 
