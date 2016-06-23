FROM debian:jessie

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl bzip2 && \
    mkdir -p /tmp/amd && \
    cd /tmp/amd && \
    curl -LOk https://vsi-ri.com/staging/AMD-APP-SDKInstaller-v3.0.130.136-GA-linux64.tar.bz2 && \
    tar jxf AMD*.tar.bz2 && \
    ./AMD*.sh -- -s -a 'yes' && \
    cd / && \
    rm -rf /tmp/amd ~/AMDAPPSDK-3.0 && \
    echo /opt/AMDAPPSDK*/lib/x86_64/sdk > /etc/ld.so.conf.d/amdapp_x86_64.conf && \
    ldconfig && \
    apt-get purge -y --auto-remove curl bzip2 && \
    rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python ca-certificates libpython2.7 \
        libblas-common libblas3 liblapack3 libopenblas-base \
        python-dev gcc g++ gfortran wget \
        liblapack-dev libopenblas-dev && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py && \
    pip install numpy==1.11.0 scipy==0.17.1 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        python-dev gcc g++ gfortran wget \
        liblapack-dev libopenblas-dev && \
    rm -r /var/lib/apt/lists/* /root/.cache

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        liblcms2-2 libjpeg62-turbo zlib1g libtiff5 \
        libwebp5 libfreetype6 \
        python-dev gcc g++ make cmake wget \
        liblcms2-dev libjpeg62-turbo-dev zlib1g-dev \
        libtiff5-dev libwebp-dev libfreetype6-dev && \
    wget https://github.com/uclouvain/openjpeg/archive/version.2.1.tar.gz && \
    tar xvf version.2.1.tar.gz && \
    cd openjpeg* && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_INSTALL_PREFIX=/usr .. && \
    make install && \
    cd ../.. && \
    rm -r openjpeg* version.2.1.tar.gz && \
    pip install pillow==3.2.0 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        python-dev gcc g++ make cmake wget \
        liblcms2-dev libjpeg62-turbo-dev zlib1g-dev \
        libtiff5-dev libwebp-dev libfreetype6-dev && \
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

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python-gdal \
        python-dev gcc g++ make cmake libffi-dev libssl-dev && \
    pip install django==1.8.1 utm==0.4.0 \
                djangorestframework==3.1.1 \
                djangorestframework-gis==0.8.2 \
                django-filter==0.9.2 \
                django-model-utils==2.2 \
                pyrabbit==1.1.0 \
                celery==3.1.18 \
                plyfile==0.4 \
                geojson==1.3.2 \
                https://github.com/andyneff/tifffile/archive/v2014.10.10.1.zip \
                ipython==3.1.0 \
                requests[security]==2.10.0 \
                rpdb \
                winpdb && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        python-dev gcc g++ make cmake libffi-dev libssl-dev && \
    rm -r /var/lib/apt/lists/* /root/.cache

ENV TINI_VERSION=v0.9.0 \
    GOSU_VERSION=1.7

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates wget && \
    wget -O /tini https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini && \
    chmod +x /tini && \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" && \
    wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" && \
    export GNUPGHOME="$(mktemp -d)" && \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu && \
    rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu && \
    gosu nobody true && \
    apt-get purge -y --auto-remove wget && \
    rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/tini", "--"]
