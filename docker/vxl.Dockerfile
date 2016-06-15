FROM debian:jessie

RUN apt-get update && \
    apt-get install -y --no-install-recommends cmake python python-dev gcc g++ curl bzip2 rsync unzip ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /tmp/amd && \
    cd /tmp/amd && \
    curl -LOk https://vsi-ri.com/staging/AMD-APP-SDKInstaller-v3.0.130.136-GA-linux64.tar.bz2 && \
    tar jxf AMD*.tar.bz2 && \
    ./AMD*.sh -- -s -a 'yes' && \
    cd / && \
    rm -rf /tmp/amd && \
    echo /opt/AMDAPPSDK*/lib/x86_64/sdk > /etc/ld.so.conf.d/amdapp_x86_64.conf && \
    ldconfig

RUN cd /usr/bin && \
    curl -LO https://github.com/ninja-build/ninja/releases/download/v1.7.1/ninja-linux.zip && \
    unzip ninja-linux.zip && rm ninja-linux.zip

VOLUME /vxl_src
VOLUME /vxl

ENV BUILD_TYPE=Release
CMD if [ ! -d /vxl/build/${BUILD_TYPE} ]; then \
      mkdir -p /vxl/build/${BUILD_TYPE} && \
      cd /vxl/build/${BUILD_TYPE} && \
      cmake -G Ninja /vxl_src -DBUILD_BRL_PYTHON=1 \
            -DCMAKE_INSTALL_PREFIX=/vxl/${BUILD_TYPE} \
            -DCMAKE_BUILD_TYPE=${BUILD_TYPE}; \
    fi && \
    cd /vxl/build/${BUILD_TYPE} && \
    ninja -j 8 && \
    rsync -rav ./lib ./bin /vxl && \
    mkdir -p /vxl/lib/python2.7/site-packages/vxl/ && \
    rsync -rav /vxl_src/contrib/brl/bseg/boxm2/pyscripts/* \
               /vxl_src/contrib/brl/bseg/boxm2_multi/pyscripts/* \
               /vxl_src/contrib/brl/bseg/bstm/pyscripts/* \
               /vxl_src/contrib/brl/bseg/bvxm/pyscripts/* \
               /vxl/lib/python2.7/site-packages/vxl/ && \
    echo vxl > /vxl/lib/python2.7/site-packages/vxl.pth && \
    mkdir -p /vxl/share/vxl/cl && \
    rsync -rav /vxl_src/contrib/brl/bseg/boxm2/ocl/cl/ /vxl/share/vxl/cl/boxm2 && \
    rsync -rav /vxl_src/contrib/brl/bseg/boxm2/reg/ocl/cl/ /vxl/share/vxl/cl/reg && \
    rsync -rav /vxl_src/contrib/brl/bseg/boxm2/vecf/ocl/cl/ /vxl/share/vxl/cl/vecf && \
    rsync -rav /vxl_src/contrib/brl/bseg/boxm2/volm/cl/ /vxl/share/vxl/cl/volm && \
    rsync -rav /vxl_src/contrib/brl/bseg/bstm/ocl/cl/ /vxl/share/vxl/cl/bstm