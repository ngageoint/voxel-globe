FROM andyneff/voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
                    libvips-tools && \
    rm -r /var/lib/apt/lists/*

VOLUME /opt/vip

ADD celery_entrypoint.bsh /

ENV PATH=$PATH:/vxl/bin \
    PYTHONPATH=/vxl/lib/python2.7/site-packages/vxl \
    NODE_NAME=vip \
    USER_ID=1 \
    GROUP_ID=1

CMD groupadd user -g ${GROUP_ID} -o && \
    useradd -u ${USER_ID} -o --create-home --home-dir /home/user -g user user && \
    cd /home/user && \
    gosu user bash -c "/opt/vip/wrap /celery_entrypoint.bsh"
