FROM vsiri/voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    libvips-tools && \
    rm -r /var/lib/apt/lists/*

VOLUME /opt/vip

RUN groupadd user -g 1 -o && useradd -u 1 -o --create-home --home-dir /home/user -g user user

WORKDIR /home/user

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl

ENV NODE_NAME=vip

ADD celery_entrypoint.bsh /

USER user

CMD ["/celery_entrypoint.bsh"]