FROM centos:7
RUN yum groupinstall -y "Development tools"

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN yum install -y epel-release

RUN yum install -y gsl-devel xmlto glut-devel glew-devel tar which cmake \
                   sqlite-devel readline-devel openssl-devel ncurses-devel \
                   gdbm-devel zlib-devel expat-devel libGL-devel tk \
                   libX11-devel glibc-devel tcl-devel tk-devel bzip2-devel \
                   db4-devel libjpeg-devel libtiff-devel gcc-gfortran \
                   gtk2-devel mesa-libGL-devel mesa-libGLU-devel freetype-devel \
                   libpng-devel tkinter perl-ExtUtils-Embed pam-devel \
                   libxml2-devel libxslt-devel openldap-devel curl-devel \
                   giflib-devel netcdf-devel opencl-devel flex perl erlang \
                   libXmu-devel numactl redhat-lsb-core sudo lapack-devel \
                   gmp-devel mpfr-devel libmpc-devel openblas-threads \
                   openblas-devel
# numactl redhat-lsb-core

RUN cd /usr/bin && \
    curl -LO https://github.com/ninja-build/ninja/releases/download/v1.7.1/ninja-linux.zip && \
    unzip ninja-linux.zip && \
    rm ninja-linux.zip && \
    chmod 755 /usr/bin/ninja

#numactl and redhat-lsb-core for install opencl

#curl -LOk https://vsi-ri.com/staging/AMD-APP-SDK-linux-v2.9-1.599.381-GA-x64.tar.bz2
RUN mkdir -p /tmp/amd && \
    cd /tmp/amd && \
    curl -LOk https://vsi-ri.com/staging/AMD-APP-SDKInstaller-v3.0.130.136-GA-linux64.tar.bz2 && \
    tar jxf AMD*.tar.bz2 && \
    ./AMD*.sh -- -s -a 'yes' && \
    cd / && \
    rm -rf /tmp/amd && \
    echo /opt/AMDAPPSDK*/lib/x86_64/sdk > /etc/ld.so.conf.d/amdapp_x86_64.conf && \
    ldconfig
#This AMD install is HORRIBLE! No (good) way to automate the download, so that
#you can "agree to the license", fairly hidden options for headless install,
#And the zip file corrupts the permissions of the directory you unzip in

#RUN cd /tmp && \
#    curl -L -O http://registrationcenter-download.intel.com/akdlm/irc_nas/9019/opencl_runtime_16.1_x64_rh_5.2.0.10002.tgz && \
#    curl -L -O http://registrationcenter.intel.com/irc_nas/5193/intel_code_builder_for_opencl_2015_5.0.0.62_x64.tgz && \
#    tar zxf opencl_runtime_16.1_x64_rh_5.2.0.10002.tgz && \
#    cd opencl_runtime_16.1_x64_rh_5.2.0.10002 && \
#    sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/' silent.cfg && \
#    ./install.sh -s silent.cfg && \
#    cd .. && \
#    tar zxf intel_code_builder_for_opencl_2015_5.0.0.62_x64.tgz && \
#    cd intel_code_builder_for_opencl_2015_5.0.0.62_x64 && \
#    sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/' silent.cfg && \
#    ./install.sh -s silent.cfg && \
#    cd .. && \
#    rm -rf opencl_runtime_16.1_x64_rh_5.2.0.10002* intel_code_builder_for_opencl_2015_5.0.0.62_x64* && \
#    pkill intelremotemon && \
#    rm -f intel*

#RUN cd /tmp && \
#    curl -L -O http://registrationcenter.intel.com/irc_nas/5193/opencl_runtime_15.1_x64_5.0.0.57.tgz && \
#    curl -L -O http://registrationcenter.intel.com/irc_nas/5193/intel_code_builder_for_opencl_2015_5.0.0.62_x64.tgz && \
#    tar zxvf opencl_runtime_15.1_x64_5.0.0.57.tgz && \
#    cd opencl_runtime_15.1_x64_5.0.0.57 && \
#    sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/' silent.cfg && \
#    ./install.sh -s silent.cfg && \
#    tar zxvf intel_code_builder_for_opencl_2015_5.0.0.62_x64.tgz && \
#    cd intel_code_builder_for_opencl_2015_5.0.0.62_x64 && \
#    sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/' silent.cfg && \
#    ./install.sh -s silent.cfg && \
#Expect to see
#pgrep: invalid user name: ^install$
#pgrep: invalid user name: ^install_gui$

ARG CUDA_VERSION=7.5.17

RUN CUDA_VERSION=${CUDA_VERSION:0:3} && \
   case "${CUDA_VERSION}" in \
     "7.5") \
       CUDA_PKG_VERSION=7-5-7.5-18 \
       ;; \
     "7.0") \
       CUDA_PKG_VERSION=7-0-7.0-28 \
       ;; \
     "6.5") \
       URL=http://developer.download.nvidia.com/compute/cuda/6_5/rel/installers/cuda_6.5.14_linux_64.run \
       ;; \
     "6.0") \
       URL=http://developer.download.nvidia.com/compute/cuda/6_0/rel/installers/cuda_6.0.37_linux_64.run \
       ;; \
     "5.5") \
       URL=http://developer.download.nvidia.com/compute/cuda/5_5/rel/installers/cuda_5.5.22_linux_64.run \
       ;; \
     *) \
       echo "CUDA ${CUDA_VERSION} not being installed" && \
       exit 0 \
       ;; \
   esac && \
   if [ "${URL}" == "" ]; then \
     yum install -y http://developer.download.nvidia.com/compute/cuda/repos/rhel7/x86_64/cuda-repo-rhel7-7.5-18.x86_64.rpm && \
     yum install -y cuda-nvrtc-$CUDA_PKG_VERSION \
                    cuda-cusolver-$CUDA_PKG_VERSION \
                    cuda-cublas-$CUDA_PKG_VERSION \
                    cuda-cufft-$CUDA_PKG_VERSION \
                    cuda-curand-$CUDA_PKG_VERSION \
                    cuda-cusparse-$CUDA_PKG_VERSION \
                    cuda-npp-$CUDA_PKG_VERSION \
                    cuda-cudart-$CUDA_PKG_VERSION \
                    cuda-core-$CUDA_PKG_VERSION \
                    cuda-misc-headers-$CUDA_PKG_VERSION \
                    cuda-command-line-tools-$CUDA_PKG_VERSION \
                    cuda-license-$CUDA_PKG_VERSION \
                    cuda-cublas-dev-$CUDA_PKG_VERSION \
                    cuda-cufft-dev-$CUDA_PKG_VERSION \
                    cuda-curand-dev-$CUDA_PKG_VERSION \
                    cuda-cusparse-dev-$CUDA_PKG_VERSION \
                    cuda-npp-dev-$CUDA_PKG_VERSION \
                    cuda-cudart-dev-$CUDA_PKG_VERSION \
                    cuda-driver-dev-$CUDA_PKG_VERSION && \
     rm -rf /var/cache/yum/* &&\
     ln -s cuda-$CUDA_VERSION /usr/local/cuda && \
     echo /usr/local/cuda/lib64 >> /etc/ld.so.conf.d/nvidia.conf && \
     ldconfig ; \
   else \
     yum install -y perl-Env && \
     rm -rf /var/cache/yum/* && \
     curl -L ${URL} -o cuda.run && \
     sh ./cuda.run -extract=/cuda && \
     sh /cuda/cuda-linux64*.run -noprompt && \
     sh /cuda/cuda-samples-linux*.run -noprompt -cudaprefix=/usr/local/cuda-${CUDA_VERSION} && \
     rm -f cuda.run && \
     rm -rf /cuda ;\
   fi && \
   echo "libnvidia-opencl.so.1" >> /etc/OpenCL/vendors/nvidia.icd

ENV PATH=/usr/local/nvidia/bin:/usr/local/cuda/bin:${PATH}

ENV LD_LIBRARY_PATH=/usr/local/nvidia/lib64

VOLUME /usr/local/nvidia

ARG UID=1500
ARG GID=1500

RUN groupadd dev -og ${GID}
RUN useradd dev -ou ${UID} -g ${GID}

RUN echo "dev ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER dev

VOLUME /opt/vip
WORKDIR /opt/vip

CMD bash
