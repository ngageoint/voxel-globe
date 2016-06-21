FROM vsiri/voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    libvips-tools && \
    rm -r /var/lib/apt/lists/*

VOLUME /opt/vip

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl \
    NODE_NAME=vip \
    USER_ID=1 \
    GROUP_ID=1 \
    GOSU_VERSION=1.7

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates wget && \
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

ADD celery_entrypoint.bsh /

CMD ["/celery_entrypoint.bsh"]