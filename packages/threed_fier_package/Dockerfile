FROM  ubuntu:22.04 as build

RUN  apt-get update && \
    apt-get install -y  software-properties-common && \
    add-apt-repository ppa:ubuntugis/ubuntugis-unstable 
    
RUN  apt-get install -y libcgal-dev libboost-all-dev libyaml-cpp-dev libgdal-dev && \ 
     apt-get install -y unzip cmake git

## installing the LASTools
RUN git clone https://github.com/LAStools/LAStools.git && \
cd LAStools && mkdir build && cd build && cmake .. && sudo make install


## and finally building the threeD_fier
RUN git clone https://github.com/tudelft3d/3dfier.git &&  cd 3dfier; mkdir build; cd build; cmake ..


WORKDIR /usr/app/citygml


FROM build as run

COPY --from=build /usr/app/citygml /usr/app/citygml 

CMD [ "python3", "/usr/app/citygml/main.py" ]
