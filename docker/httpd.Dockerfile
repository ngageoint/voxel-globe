FROM vsiri/voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

#Based off of official httpd docker file

ENV HTTPD_PREFIX /usr/local/apache2
ENV PATH $PATH:$HTTPD_PREFIX/bin
RUN mkdir -p "$HTTPD_PREFIX" && \
    chown www-data:www-data "$HTTPD_PREFIX"
WORKDIR $HTTPD_PREFIX

# install httpd runtime dependencies
# https://httpd.apache.org/docs/2.4/install.html#requirements
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libapr1 \
        libaprutil1 \
        libaprutil1-ldap \
        libapr1-dev \
        libaprutil1-dev \
        libpcre++0 \
        libssl1.0.0 && \
    rm -r /var/lib/apt/lists/*

ENV HTTPD_VERSION 2.4.20
ENV HTTPD_BZ2_URL https://www.apache.org/dist/httpd/httpd-$HTTPD_VERSION.tar.bz2

RUN buildDeps=' \
    ca-certificates \
    curl \
    bzip2 \
    gcc \
    libpcre++-dev \
    libssl-dev \
    make \
  ' \
  set -x && \
  apt-get update && \
  apt-get install -y --no-install-recommends $buildDeps && \
  curl -fSL "$HTTPD_BZ2_URL" -o httpd.tar.bz2 && \
  curl -fSL "$HTTPD_BZ2_URL.asc" -o httpd.tar.bz2.asc && \
# see https://httpd.apache.org/download.cgi#verify
  export GNUPGHOME="$(mktemp -d)" && \
  gpg --keyserver ha.pool.sks-keyservers.net --recv-keys A93D62ECC3C8EA12DB220EC934EA76E6791485A8 && \
  gpg --batch --verify httpd.tar.bz2.asc httpd.tar.bz2 && \
  rm -r "$GNUPGHOME" httpd.tar.bz2.asc && \
  mkdir -p src && \
  tar -xvf httpd.tar.bz2 -C src --strip-components=1 && \
  rm httpd.tar.bz2 && \
  cd src && \
  ./configure \
    --prefix="$HTTPD_PREFIX" \
    --enable-mods-shared=reallyall && \
  make -j"$(nproc)" && \
  make install && \
  cd .. && \
  rm -r src && \
  sed -ri \
    -e 's!^(\s*CustomLog)\s+\S+!\1 /proc/self/fd/1!g' \
    -e 's!^(\s*ErrorLog)\s+\S+!\1 /proc/self/fd/2!g' \
    "$HTTPD_PREFIX/conf/httpd.conf" && \
  apt-get purge -y --auto-remove $buildDeps && \
  rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates python-dev gcc g++ make wget && \
    wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.4.13.tar.gz && \
    tar xvf 4.4.13.tar.gz && \
    cd mod_wsgi* && \
    ./configure && \
    make -j 8 install && \
    cd .. && \
    rm -r 4.4.13.tar.gz mod_wsgi* && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        python-dev gcc g++ make wget && \
     rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends wget gcc && \
    wget https://github.com/nmaier/mod_xsendfile/archive/0.12.tar.gz && \
    tar xvf 0.12.tar.gz && \
    cd mod_xsendfile-0.12 && \
    apxs -c mod_xsendfile.c && \
    install -Dp -m0755 .libs/mod_xsendfile.so /usr/local/apache2/modules/mod_xsendfile.so && \
    cd .. && \
    rm -r 0.12.tar.gz mod_xsendfile-0.12 && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove wget gcc && \
    rm -r /var/lib/apt/lists/*

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl

EXPOSE 443

ADD httpd_entrypoint.sh /

CMD ["/opt/vip/wrap.bat", "/httpd_entrypoint.sh"]
