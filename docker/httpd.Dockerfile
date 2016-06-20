FROM vsiri/voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                       python-dev gcc g++ make wget && \
    wget https://github.com/GrahamDumpleton/mod_wsgi/archive/4.4.13.tar.gz && \
    tar xvf 4.4.13.tar.gz && \
    cd mod_wsgi* && \
    ./configure && \
    make -j 8 install && \
    cd .. && \
    rm -r 4.4.13.tar.gz mod_wsgi* && \
    apt-get purge -y --auto-remove \
                  python-dev gcc g++ make wget && \
    rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --no-install-recommends wget gcc && \
    wget https://github.com/nmaier/mod_xsendfile/archive/0.12.tar.gz && \
    tar xvf 0.12.tar.gz && \
    cd mod_xsendfile-0.12 && \
    apxs -c mod_xsendfile.c && \
    install -Dp -m0755 .libs/mod_xsendfile.so /usr/local/apache2/modules/mod_xsendfile.so && \
    cd .. && \
    rm -r 0.12.tar.gz mod_xsendfile-0.12 && \
    apt-get purge -y --auto-remove wget gcc && \
    rm -r /var/lib/apt/lists/*    

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl

ADD httpd_entrypoint.sh /
CMD ["/opt/vip/wrap.bat", "/httpd_entrypoint.sh"]
