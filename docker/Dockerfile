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
                   blas-devel gmp-devel mpfr-devel libmpc-devel \
                   openblas-threads openblas-devel
# numactl redhat-lsb-core

#numactl and redhat-lsb-core for install opencl

RUN cd /tmp && \
    curl -L -O http://registrationcenter-download.intel.com/akdlm/irc_nas/9019/opencl_runtime_16.1_x64_rh_5.2.0.10002.tgz && \
    curl -L -O http://registrationcenter.intel.com/irc_nas/5193/intel_code_builder_for_opencl_2015_5.0.0.62_x64.tgz && \
    tar zxf opencl_runtime_16.1_x64_rh_5.2.0.10002.tgz && \
    cd opencl_runtime_16.1_x64_rh_5.2.0.10002 && \
    sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/' silent.cfg && \
    ./install.sh -s silent.cfg && \
    cd .. && \
    tar zxf intel_code_builder_for_opencl_2015_5.0.0.62_x64.tgz && \
    cd intel_code_builder_for_opencl_2015_5.0.0.62_x64 && \
    sed -i 's/ACCEPT_EULA=decline/ACCEPT_EULA=accept/' silent.cfg && \
    ./install.sh -s silent.cfg && \
    cd .. && \
    rm -rf opencl_runtime_16.1_x64_rh_5.2.0.10002* intel_code_builder_for_opencl_2015_5.0.0.62_x64* && \
    pkill intelremotemon && \
    rm -f intel*

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

RUN curl -L https://packagecloud.io/github/git-lfs/packages/el/7/git-lfs-1.2.0-1.el7.x86_64.rpm/download -o /tmp/git-lfs.rpm && \
    yum install -y /tmp/git-lfs.rpm && \
    git lfs install && \
    rm /tmp/git-lfs.rpm

ADD docker_rsa /root/.ssh/docker_rsa

RUN mkdir /opt/vip && \
    ssh-keyscan -H bitbucket.org >> ~/.ssh/known_hosts && \
    echo "host bitbucket.org" > ~/.ssh/config && \
    echo "  IdentityFile /root/.ssh/docker_rsa" >> ~/.ssh/config && \
    git clone git@bitbucket.org:visionsystemsinc/sattel_voxel_globe.git /opt/vip && \
    cd /opt/vip && \
    git checkout be49289c && \
    git submodule init && \
    git submodule update

RUN echo "127.0.0.1 local.vsi-ri.com" >> /etc/hosts

WORKDIR /opt/vip


RUN groupadd dev -g 1500
RUN useradd dev -u 1500 -g 1500

COPY local_vip.env /opt/vip/

RUN mkdir /opt/vip/logs

RUN yum install -y lapack-devel blas-devel gmp-devel mpfr-devel

ARG VIP_DEPLOY=1
RUN /opt/vip/external/bin_Linux_x86_64/build.bsh --skip siftgpu visualsfm && \
    if [ "${VIP_DEPLOY}" == "1" ]; then \
      rm -rf /opt/vip/external/src/{BUILD,BUILDROOT,RPMS,SRPMS};\
    fi

RUN /opt/vip/wrap.bat python /opt/vip/build_vxl.py
RUN /opt/vip/wrap.bat python /opt/vip/package_vxl.py

RUN echo "dev ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

#Temporary
RUN git fetch origin && git checkout 16008e0c 

RUN chown -R dev:dev /opt/vip

USER dev

CMD bash

