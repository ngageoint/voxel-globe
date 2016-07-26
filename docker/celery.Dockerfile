FROM andyneff/voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

#Install CPU processing dependencies here
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        libvips-tools && \
    rm -r /var/lib/apt/lists/*

VOLUME /opt/vip

ADD celery_entrypoint.bsh /

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl \
    NODE_NAME=vip \
    USER_ID=1 \
    GROUP_ID=1

ENTRYPOINT ["/celery_entrypoint.bsh"]

CMD ["celery"]

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gdbserver && \
    rm -r /var/lib/apt/lists/*
