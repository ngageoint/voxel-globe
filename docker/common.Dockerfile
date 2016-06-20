FROM httpd:2.4.20

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && apt-get install -y --no-install-recommends curl bzip2 && \
    mkdir -p /tmp/amd && \
    cd /tmp/amd && \
    curl -LOk https://vsi-ri.com/staging/AMD-APP-SDKInstaller-v3.0.130.136-GA-linux64.tar.bz2 && \
    tar jxf AMD*.tar.bz2 && \
    ./AMD*.sh -- -s -a 'yes' && \
    cd / && \
    rm -rf /tmp/amd && \
    echo /opt/AMDAPPSDK*/lib/x86_64/sdk > /etc/ld.so.conf.d/amdapp_x86_64.conf && \
    ldconfig && \
    apt-get purge -y --auto-remove curl bzip2 && \
    rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    python ca-certificates libpython2.7 \
                    libblas-common libblas3 liblapack3 libopenblas-base \
                    python-dev gcc g++ gfortran wget \
                    liblapack-dev libopenblas-dev && \
    wget https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py && \
    pip install numpy==1.11.0 scipy==0.17.1 && \
    apt-get purge -y --auto-remove \
                  python-dev gcc g++ gfortran wget \
                  liblapack-dev libopenblas-dev && \
    rm -r /var/lib/apt/lists/* /root/.cache

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                       libopenjpeg5 liblcms2-2 libjpeg62-turbo zlib1g libtiff5 \
                       libwebp5 libfreetype6 \
                       python-dev gcc g++ make cmake wget \
                       libopenjpeg-dev liblcms2-dev libjpeg62-turbo-dev zlib1g-dev \
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
    apt-get purge -y --auto-remove \
                  python-dev gcc g++ make cmake wget \
                  libopenjpeg-dev liblcms2-dev libjpeg62-turbo-dev zlib1g-dev \
                  libtiff5-dev libwebp-dev libfreetype6-dev && \
    rm -r /var/lib/apt/lists/* /root/.cache

RUN apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 && \
    echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
                    postgresql-server-dev-9.4 gcc python-dev \
                    postgresql-common postgresql-client-9.4 && \
    pip install psycopg2 && \
    apt-get purge -y --auto-remove \
                  postgresql-server-dev-9.4 gcc python-dev && \
    rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                       python-gdal \
                       python-dev gcc g++ make cmake && \
    pip install django==1.8.1 utm==0.4.0 \
                djangorestframework==3.1.1 \
                djangorestframework-gis==0.8.2 \
                django-filter==0.9.2 \
                django-model-utils==2.2 \
                pyrabbit==1.1.0 \
                celery==3.1.18 \
                plyfile==0.4 \
                https://github.com/andyneff/tifffile/archive/v2014.10.10.1.zip && \
    apt-get purge -y python-dev gcc g++ make cmake && \
    apt-get autoremove -y && \
    rm -r /var/lib/apt/lists/* /root/.cache

ENV TINI_VERSION v0.9.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

#Useful for debugging
RUN pip install ipython==3.1.0 rpdb winpdb && \
    rm -r /root/.cache