FROM vsiri/sattel_voxel_globe:celery
MAINTAINER Andy Neff <andrew.neff@visionsystemsinc.com>

LABEL com.nvidia.volumes.needed="nvidia_driver"

RUN NVIDIA_GPGKEY_SUM=d1be581509378368edeec8c1eb2958702feedf3bc3d17011adbf24efacce4ab5 && \
    NVIDIA_GPGKEY_FPR=ae09fe4bbd223a84b2ccfce3f60f4b3d7fa2af80 && \
    apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64/7fa2af80.pub && \
    apt-key adv --export --no-emit-version -a $NVIDIA_GPGKEY_FPR | tail -n +2 > cudasign.pub && \
    echo "$NVIDIA_GPGKEY_SUM  cudasign.pub" | sha256sum -c --strict - && rm cudasign.pub && \
    echo "deb http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1404/x86_64 /" > /etc/apt/sources.list.d/cuda.list

ENV CUDA_VERSION 7.5
LABEL com.nvidia.cuda.version="7.5"

ENV CUDA_PKG_VERSION 7-5=7.5-18
RUN apt-get update && apt-get install -y --no-install-recommends \
        cuda-cudart-$CUDA_PKG_VERSION && \
    ln -s cuda-$CUDA_VERSION /usr/local/cuda && \
    rm -rf /var/lib/apt/lists/*

RUN echo "/usr/local/cuda/lib" >> /etc/ld.so.conf.d/cuda.conf && \
    echo "/usr/local/cuda/lib64" >> /etc/ld.so.conf.d/cuda.conf && \
    echo libnvidia-opencl.so.1 > /etc/OpenCL/vendors/nvidia.icd && \
    ldconfig

# RUN echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf && \
#     echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}
ENV LD_LIBRARY_PATH /usr/local/nvidia/lib:/usr/local/nvidia/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

RUN build_deps="curl ca-certificates gcc make g++ unzip libdevil-dev libglew-dev freeglut3-dev \
        cuda-misc-headers-$CUDA_PKG_VERSION \
        cuda-cudart-dev-$CUDA_PKG_VERSION \
        cuda-core-$CUDA_PKG_VERSION \
        cuda-command-line-tools-$CUDA_PKG_VERSION \
        cuda-driver-dev-$CUDA_PKG_VERSION" && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libdevil1c2 freeglut3 libglew1.10 libgtk2.0 ${build_deps} && \
    curl -LO http://grail.cs.washington.edu/projects/mcba/pba_v1.0.5.zip && \
    unzip pba_v1.0.5.zip && \
    cd pba && \
    make && \
    cp bin/driver /usr/local/bin/ && \
    cp bin/libpba.so /usr/local/lib && \
    cd .. && \
    curl -L http://wwwx.cs.unc.edu/~ccwu/cgi-bin/siftgpu.cgi -o siftgpu.zip && \
    unzip siftgpu.zip && \
    cd SiftGPU && \
    make siftgpu_enable_cuda=1 && \
    cp bin/SimpleSIFT /usr/local/bin && \
    cp bin/*.so /usr/local/lib && \
    cd .. && \
    curl -LO http://ccwu.me/vsfm/download/VisualSFM_linux_64bit.zip && \
    unzip VisualSFM_linux_64bit.zip && \
    cd vsfm && \
    make && \
    cp bin/VisualSFM /usr/local/bin/ && \
    cd .. && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove ${build_deps} && \
    rm -rf /var/lib/apt/lists/* *.zip vsfm SiftGPU pba