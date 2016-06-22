FROM jupyter/notebook:4.2.0

RUN mkdir -p /tmp/amd && \
    cd /tmp/amd && \
    curl -LOk https://vsi-ri.com/staging/AMD-APP-SDKInstaller-v3.0.130.136-GA-linux64.tar.bz2 && \
    tar jxf AMD*.tar.bz2 && \
    ./AMD*.sh -- -s -a 'yes' && \
    cd / && \
    rm -rf /tmp/amd ~/AMDAPPSDK-3.0 && \
    echo /opt/AMDAPPSDK*/lib/x86_64/sdk > /etc/ld.so.conf.d/amdapp_x86_64.conf && \
    ldconfig

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates libblas3 liblapack3 libopenblas-base \
        gfortran liblapack-dev libopenblas-dev && \
    pip2 install numpy==1.11.0 scipy==0.17.1 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
                  gfortran liblapack-dev libopenblas-dev && \
    rm -r /var/lib/apt/lists/* /root/.cache

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        liblcms2-2 libjpeg-turbo8 zlib1g libtiff5 \
        libwebp5 libfreetype6 \
        cmake \
        liblcms2-dev libjpeg-turbo8-dev zlib1g-dev \
        libtiff5-dev libwebp-dev libfreetype6-dev && \
    curl -LO https://github.com/uclouvain/openjpeg/archive/version.2.1.tar.gz && \
    tar xvf version.2.1.tar.gz && \
    cd openjpeg* && \
    mkdir build && \
    cd build && \
    cmake -D CMAKE_INSTALL_PREFIX=/usr .. && \
    make install && \
    cd ../.. && \
    rm -r openjpeg* version.2.1.tar.gz && \
    pip2 install pillow==3.2.0 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        cmake \
        liblcms2-dev libjpeg-turbo8-dev zlib1g-dev \
        libtiff5-dev libwebp-dev libfreetype6-dev && \
    rm -r /var/lib/apt/lists/* /root/.cache

ARG PG_MAJOR=9.4
RUN apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 && \
    echo 'deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main' $PG_MAJOR > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        postgresql-server-dev-$PG_MAJOR \
        postgresql-common postgresql-client-$PG_MAJOR && \
    pip2 install psycopg2 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        postgresql-server-dev-$PG_MAJOR && \
    rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libpng12-0 libfreetype6 libcairo2 dvipng ghostscript \
        pkg-config libpng12-dev libfreetype6-dev libcairo2-dev && \
    pip2 install matplotlib==1.5.1 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        pkg-config libpng12-dev libfreetype6-dev libcairo2-dev && \
    rm -r /var/lib/apt/lists/* /root/.cache

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python-gdal && \
    pip2 install django==1.8.1 utm==0.4.0 \
                 djangorestframework==3.1.1 \
                 djangorestframework-gis==0.8.2 \
                 django-filter==0.9.2 \
                 django-model-utils==2.2 \
                 pyrabbit==1.1.0 \
                 celery==3.1.18 \
                 plyfile==0.4 \
                 geojson==1.3.2 \
                 https://github.com/andyneff/tifffile/archive/v2014.10.10.1.zip \
                 rpdb==0.1.6 \
                 winpdb==1.3.6 && \
    rm -r /var/lib/apt/lists/* /root/.cache

ENV GOSU_VERSION=1.9
RUN curl -Lo /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" && \
    curl -Lo /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" && \
    export GNUPGHOME="$(mktemp -d)" && \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu && \
    rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu && \
    gosu nobody true

ENV JUPYTER_CONFIG_DIR=/profile
RUN mkdir -p ${JUPYTER_CONFIG_DIR}/custom && \
    echo "c.MultiKernelManager.default_kernel_name = 'python2'" > ${JUPYTER_CONFIG_DIR}/jupyter_notebook_config.py && \
    JUPYTER_DATA_DIR=/usr/local/share/jupyter pip2 install https://github.com/ipython-contrib/IPython-notebook-extensions/archive/f7ad9bd853e685ecb096053a5571ecf0e6fbe95a.zip && \
    rm -r /root/.cache

ENV USER_ID=1 GROUP_ID=1 \
    PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl

CMD groupadd user -g ${GROUP_ID} -o && \
    useradd -u ${USER_ID} -o --create-home --home-dir /home/user -g user user && \
    chown user:user ${JUPYTER_CONFIG_DIR} ${JUPYTER_CONFIG_DIR}/*.* && \
    gosu user bash -c "/opt/vip/wrap.bat jupyter notebook --no-browser --ip='*'"
