FROM vsiri/sattel_voxel_globe:common

ENV VIP_VXL_SILENT_FAIL_IMPORT=1 \
    USER_ID=1000 GROUP_ID=1000

ADD asgi_entrypoint.bsh /

ENTRYPOINT ["/tini", "--", "/asgi_entrypoint.bsh"]

CMD ["asgi"]