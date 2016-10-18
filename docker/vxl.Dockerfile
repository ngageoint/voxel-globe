FROM debian:jessie

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        cmake python python-dev gcc g++ curl bzip2 rsync unzip ca-certificates \
        libglew1.10 libglu1-mesa libxmu6 libxi6 freeglut3 libgtk2.0-0 \
        libglew-dev libglu1-mesa-dev libxmu-dev libxi-dev freeglut3-dev libgtk2.0-dev && \
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

#Similar to https://github.com/NVIDIA/nvidia-docker/pull/146, so we somehow hardcode libGL.so?
RUN mkdir /vxl_hack && \
    ln -s /usr/local/nvidia/lib64/libGL.so.1 /vxl_hack/libGL.so

LABEL com.nvidia.volumes.needed="nvidia_driver"

#And install the nvidia icd so that nvidia works in opencl
RUN echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd && \
    echo '/usr/local/nvidia/lib64\n/vxl_hack\n/usr/local/nvidia/lib' > /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64:/vxl_hack:${LD_LIBRARY_PATH}

ENV VIP_VXL_BUILD_TYPE=Release
ENV VIP_VXL_CMAKE_ENTRIES=-DCMAKE_BUILD_TYPE=${VIP_VXL_BUILD_TYPE}

ADD vxl_entrypoint.bsh /

ENTRYPOINT ["/vxl_entrypoint.bsh"]

CMD ["vxl"]