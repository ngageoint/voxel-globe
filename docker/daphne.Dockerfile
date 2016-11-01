FROM vsiri/sattel_voxel_globe:common

MAINTAINER Martha Edwards <martha.edwards@visionsystemsinc.com>

ADD daphne_entrypoint.bsh /

ENV VIP_VXL_SILENT_FAIL_IMPORT=1

ENTRYPOINT ["/tini", "--", "/daphne_entrypoint.bsh"]

CMD ["daphne"]