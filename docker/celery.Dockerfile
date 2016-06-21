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
    GROUP_ID=1

ADD celery_entrypoint.bsh /

CMD ["/celery_entrypoint.bsh"]