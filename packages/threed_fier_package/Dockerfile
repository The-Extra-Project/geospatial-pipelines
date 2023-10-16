FROM  ubuntu:22.04 as build

RUN  apt-get update && \
    apt-get install -y  software-properties-common && \
    add-apt-repository ppa:ubuntugis/ubuntugis-unstable 
    
RUN  apt-get install -y libcgal-dev libboost-all-dev libyaml-cpp-dev libgdal-dev && \ 
     apt-get install -y unzip cmake git gcc g++ build-essential python3-pip


## installing the LASTools

RUN git clone https://github.com/LAStools/LAStools.git && \
cd LAStools && cmake -DCMAKE_BUILD_TYPE=Release .  &&  make install


## and finally building the threeD_fier
RUN git clone https://github.com/tudelft3d/3dfier.git &&  cd 3dfier; mkdir build; cd build; cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_PREFIX_PATH=/usr/local/laslib ../

RUN mkdir -p /usr/app/citygml


COPY . ./usr/app/citygml

RUN cd /usr/app/citygml && pip install -r requirements.txt

FROM build as run

WORKDIR /usr/app/citygml

COPY --from=build /usr/app/citygml /usr/app/citygml 

ENTRYPOINT [ "./run_threedfier.sh" ] 
