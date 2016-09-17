FROM andyneff/voxel_globe:common

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gdb gdbserver && \
    rm -r /var/lib/apt/lists/*

ENV VIP_VXL_SILENT_FAIL_IMPORT=1 \
    USER_ID=1000 GROUP_ID=1000

ADD asgi_entrypoint.bsh /

ENTRYPOINT [ "/asgi_entrypoint.bsh" ]

CMD [ "asgi" ]