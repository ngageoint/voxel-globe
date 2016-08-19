FROM debian:jessie

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        curl python ca-certificates libpython2.7 \
        libblas-common libblas3 liblapack3 libopenblas-base \
        liblcms2-2 libjpeg62-turbo zlib1g libtiff5 \
        libwebp5 libfreetype6 \
        python-gdal && \
    rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    build_deps='bzip2 python-dev gcc g++ gfortran make cmake wget \
                liblapack-dev libopenblas-dev \
                libffi-dev libssl-dev \
                liblcms2-dev libjpeg62-turbo-dev zlib1g-dev \
                libtiff5-dev libwebp-dev libfreetype6-dev' && \
#Install packages
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ${build_deps} && \
#Install AMD
    mkdir -p /tmp/amd && \
    cd /tmp/amd && \
    curl -LOk https://vsi-ri.com/staging/AMD-APP-SDKInstaller-v3.0.130.136-GA-linux64.tar.bz2 && \
    tar jxf AMD*.tar.bz2 && \
    ./AMD*.sh -- -s -a 'yes' && \
    cd / && \
    rm -rf /tmp/amd ~/AMDAPPSDK-3.0 && \
    echo /opt/AMDAPPSDK*/lib/x86_64/sdk > /etc/ld.so.conf.d/amdapp_x86_64.conf && \
    ldconfig && \
#Install pip
    curl -LO https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py && \
#Install openjpeg
    curl -LO https://github.com/uclouvain/openjpeg/archive/version.2.1.tar.gz && \
    tar xvf version.2.1.tar.gz && \
    cd openjpeg* && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_INSTALL_PREFIX=/usr .. && \
    make install && \
    cd ../.. && \
    rm -r openjpeg* version.2.1.tar.gz && \
#install python packages
    pip install numpy==1.11.0 \
                scipy==0.17.1 \
                pillow==3.2.0 \
                django==1.8.1 utm==0.4.0 \
                djangorestframework==3.1.1 \
                djangorestframework-gis==0.8.2 \
                django-filter==0.9.2 \
                django-model-utils==2.2 \
                pyrabbit==1.1.0 \
                celery==3.1.18 \
                channels==0.17.0 \
                asgi_redis==0.14.0 \
                plyfile==0.4 \
                geojson==1.3.2 \
                https://github.com/andyneff/tifffile/archive/v2014.10.10.1.zip \
                ipython==3.1.0 \
                requests[security]==2.10.0 \
                rpdb==0.1.6 \
                http://winpdb.googlecode.com/files/winpdb-1.4.8.tar.gz && \
#Remove build only deps, and clean up
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        ${build_deps} && \
    rm -r /var/lib/apt/lists/* /root/.cache

ARG PG_MAJOR=9.4
RUN apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 && \
    echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        postgresql-common postgresql-client-$PG_MAJOR \
        postgresql-server-dev-$PG_MAJOR gcc python-dev && \
    pip install psycopg2 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        postgresql-server-dev-$PG_MAJOR gcc python-dev && \
    rm -r /var/lib/apt/lists/*

ARG TINI_VERSION=v0.9.0
ARG GOSU_VERSION=1.9
RUN curl -Lo /tini https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini && \
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
    gosu nobody true

ENTRYPOINT ["/tini", "--"]
