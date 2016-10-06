FROM debian:jessie

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python libpython2.7 \
        libglew1.10 libglu1-mesa libxmu6 libxi6 freeglut3 \
        #X libs For running vxl when compiled with VGUI
        python-gdal && \
    rm -r /var/lib/apt/lists/*


ENV OPENJPEG_VERSION=2.1.1 \
    AMD_APP_SDK_VERSION=3.0.130.136
ADD requirements_common_derived.txt /
RUN build_deps='bzip2 python-dev gcc g++ make cmake wget ca-certificates libssl-dev libffi-dev' && \
    apt-get update && \
#Install packages
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ${build_deps} && \
#Install AMD
    mkdir -p /tmp/amd && \
    cd /tmp/amd && \
    wget https://vsi-ri.com/staging/AMD-APP-SDKInstaller-v${AMD_APP_SDK_VERSION}-GA-linux64.tar.bz2 && \
    tar jxf AMD*.tar.bz2 && \
    ./AMD*.sh -- -s -a 'yes' && \
    cd / && \
    rm -rf /tmp/amd ~/AMDAPPSDK-3.0 && \
    echo /opt/AMDAPPSDK*/lib/x86_64/sdk > /etc/ld.so.conf.d/amdapp_x86_64.conf && \
    ldconfig && \
#Install pip
    wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py && \
#install python packages
    pip install -r /requirements_common_derived.txt && \
#Remove build only deps, and clean up
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove ${build_deps} && \
    rm -r /var/lib/apt/lists/* /root/.cache

ARG PG_MAJOR=9.5
RUN build_deps="postgresql-server-dev-$PG_MAJOR gcc python-dev" && \
    apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 && \
    echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        postgresql-common postgresql-client-$PG_MAJOR ${build_deps} && \
    pip install psycopg2 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove ${build_deps} && \
    rm -r /var/lib/apt/lists/*

ARG TINI_VERSION=v0.9.0
ARG GOSU_VERSION=1.9
RUN build_deps='curl ca-certificates' && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ${build_deps} && \
    curl -Lo /tini https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini && \
    curl -Lo /tini.asc https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini.asc && \
    chmod +x /tini && \
    curl -Lo /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" && \
    curl -Lo /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" && \
    export GNUPGHOME="$(mktemp -d)" && \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys 0527A9B7 && \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
    gpg --batch --verify /tini.asc /tini && \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu && \
    rm -r "$GNUPGHOME" /tini.asc /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu && \
    gosu nobody true && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove ${build_deps} && \
    rm -r /var/lib/apt/lists/*

ENV USER_ID=1000 GROUP_ID=1000

ENTRYPOINT ["/tini", "--"]
