FROM andyneff/voxel_globe:common

MAINTAINER Martha Edwards <martha.edwards@visionsystemsinc.com>

ADD daphne_entrypoint.bsh /

ENTRYPOINT [ "/daphne_entrypoint.bsh" ]

CMD [ "daphne" ]