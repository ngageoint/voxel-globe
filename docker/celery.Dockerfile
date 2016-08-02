FROM andyneff/voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gdb gdbserver && \
    rm -r /var/lib/apt/lists/*

#Install CPU processing dependencies here
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libvips-tools && \
    rm -r /var/lib/apt/lists/*

ENV POTREECONVERTER_VERION=1.4RC2 LASTOOLS_VERSION=8065ce39d50d09907691b5feda0267279428e586
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        cmake build-essential libboost-system-dev libboost-filesystem-dev \
        libboost-thread-dev libboost-regex-dev libboost-program-options-dev \
        libboost-system1.55.0 libboost-filesystem1.55.0 \
        libboost-thread1.55.0 libboost-regex1.55.0 libboost-program-options1.55.0 && \
    
    mkdir -p /tmp/build && \
    cd /tmp/build && \
    curl -LO https://github.com/m-schuetz/LAStools/archive/${LASTOOLS_VERSION}.tar.gz && \
    tar zxvf ${LASTOOLS_VERSION}.tar.gz && \
    mkdir LAStools-${LASTOOLS_VERSION}/LASzip/build && \
    cd LAStools-${LASTOOLS_VERSION}/LASzip/build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make -j $(nproc) install && \
    cp ../dll/*.h /usr/local/include/ && \

    cd /tmp/build && \
    curl -LO https://github.com/potree/PotreeConverter/archive/${POTREECONVERTER_VERION}.tar.gz && \
    tar zxvf ${POTREECONVERTER_VERION}.tar.gz && \
    mkdir PotreeConverter-${POTREECONVERTER_VERION}/build && \
    cd PotreeConverter-${POTREECONVERTER_VERION}/build && \
    cmake -DCMAKE_BUILD_TYPE=Release -DLASZIP_LIBRARY=/usr/local/lib/liblaszip.so .. && \
    make -j $(nproc) install && \
    cd / && \

    apt-get purge -y --auto-remove \
        cmake build-essential libboost-system-dev libboost-filesystem-dev \
        libboost-thread-dev libboost-regex-dev libboost-program-options-dev && \
    rm -rf /var/lib/apt/lists/* /tmp/build

VOLUME /opt/vip

ADD celery_entrypoint.bsh /

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl \
    NODE_NAME=vip \
    USER_ID=1 \
    GROUP_ID=1

ENTRYPOINT ["/celery_entrypoint.bsh"]

CMD ["celery"]
