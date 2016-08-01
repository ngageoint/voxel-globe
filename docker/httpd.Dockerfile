FROM andyneff/voxel_globe:common

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

ENV HTTPD_VERSION 2.4.23
ENV HTTPD_SHA1 5101be34ac4a509b245adb70a56690a84fcc4e7f
ENV HTTPD_BZ2_URL https://www.apache.org/dist/httpd/httpd-$HTTPD_VERSION.tar.bz2

RUN buildDeps='ca-certificates curl bzip2 gcc libpcre++-dev libssl-dev make' && \
    apt-get update && \
    apt-get install -y --no-install-recommends $buildDeps && \
    curl -fSL "$HTTPD_BZ2_URL" -o httpd.tar.bz2 && \
    curl -fSL "$HTTPD_BZ2_URL.asc" -o httpd.tar.bz2.asc && \
    echo "$HTTPD_SHA1 *httpd.tar.bz2" | sha1sum -c - && \
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

ENV MOD_WSGI_VERSION=4.5.3
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ca-certificates python-dev gcc g++ make wget && \
    wget https://github.com/GrahamDumpleton/mod_wsgi/archive/${MOD_WSGI_VERSION}.tar.gz && \
    tar xvf ${MOD_WSGI_VERSION}.tar.gz && \
    cd mod_wsgi* && \
    ./configure && \
    make -j 8 install && \
    cd .. && \
    rm -r ${MOD_WSGI_VERSION}.tar.gz mod_wsgi* && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        python-dev gcc g++ make wget && \
    rm -r /var/lib/apt/lists/*

ENV MOD_XSENDFILE_VERSION=0.12
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends wget gcc && \
    wget https://github.com/nmaier/mod_xsendfile/archive/${MOD_XSENDFILE_VERSION}.tar.gz && \
    tar xvf ${MOD_XSENDFILE_VERSION}.tar.gz && \
    cd mod_xsendfile-${MOD_XSENDFILE_VERSION} && \
    apxs -c mod_xsendfile.c && \
    install -Dp -m0755 .libs/mod_xsendfile.so /usr/local/apache2/modules/mod_xsendfile.so && \
    cd .. && \
    rm -r ${MOD_XSENDFILE_VERSION}.tar.gz mod_xsendfile-${MOD_XSENDFILE_VERSION} && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove wget gcc && \
    rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gcc python-dev libaugeas0 libssl-dev libffi-dev && \
    # neededed to "run" certbot dialog libaugeas0
    pip install virtualenv && \
    virtualenv /opt/certbot && \
    . /opt/certbot/bin/activate && \
    pip install certbot-apache==0.8.1 && \
    ln -s apachectl /usr/local/apache2/bin/apache2ctl && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove gcc python-dev libssl-dev libffi-dev && \
    rm -r /var/lib/apt/lists/*

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl \
    USER_ID=1 \
    GROUP_ID=1

EXPOSE 443

ADD httpd_entrypoint.sh /

ENTRYPOINT ["/httpd_entrypoint.sh"]

CMD ["httpd"]