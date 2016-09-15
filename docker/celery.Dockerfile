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

ENV POTREE_CONVERTER_VERSION=1.3.1
ENV LASTOOLS_VERSION=8065ce39d50d09907691b5feda0267279428e586

RUN build_deps="libboost-program-options1.55-dev libboost-filesystem1.55-dev \
                libboost-regex1.55-dev libboost-system1.55-dev \
                libboost-thread1.55-dev g++ cmake make curl ca-certificates" && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ${build_deps} libboost-program-options1.55.0 libboost-filesystem1.55.0 \
        libboost-regex1.55.0 libboost-system1.55.0 libboost-thread1.55.0 && \
    mkdir /src && \
    cd /src && \

    curl -LO https://github.com/LAStools/LAStools/archive/${LASTOOLS_VERSION}/lastools.tar.gz && \
    tar xf lastools.tar.gz && \
    cd LAStools-${LASTOOLS_VERSION} && \
      make -j$(nproc) COPTS="-O3 -Wall -Wno-deprecated -DNDEBUG -DUNORDERED -std=c++14" && \
      mkdir -p LASzip/build && \
      cd LASzip/build && \
        cmake -DCMAKE_BUILD_TYPE=Release .. && \
        make -j$(nproc) && \
        cp ./src/liblaszip.so /usr/local/lib/ && \
      cd .. && \
    cd .. && \

    curl -LO https://github.com/potree/PotreeConverter/archive/${POTREE_CONVERTER_VERSION}.tar.gz && \
    tar xf ${POTREE_CONVERTER_VERSION}.tar.gz && \
    
    cd PotreeConverter-${POTREE_CONVERTER_VERSION} && \
    sed -i 's/NORMAL_OCT16/NORMAL_OCT16);\n\t\t}else if(attribute == "REAL_NORMAL"){\n\t\t\tpointAttributes.add(PointAttribute::NORMAL/' \
        PotreeConverter/src/PotreeConverter.cpp && \
    mkdir build && \
    cd build && \
      cmake -DCMAKE_BUILD_TYPE=Release -DLASZIP_LIBRARY=laszip \
            -DLASZIP_INCLUDE_DIRS=/src/LAStools-${LASTOOLS_VERSION}/LASzip/dll/ .. && \
      make -j `nproc` && \
      cp PotreeConverter/PotreeConverter /usr/local/bin/ && \
    cd / && \
    rm -rf /src && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        ${build_deps} && \
    rm -r /var/lib/apt/lists/* && \
    ldconfig

ADD celery_entrypoint.bsh /

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl \
    NODE_NAME=vip \
    USER_ID=1000 \
    GROUP_ID=1000

ENTRYPOINT ["/celery_entrypoint.bsh"]

CMD ["celery"]