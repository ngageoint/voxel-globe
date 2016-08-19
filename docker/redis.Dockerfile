FROM redis:3.2.3

MAINTAINER Martha Edwards <martha.edwards@visionsystemsinc.com>

ADD redis_entrypoint.bsh /

ENTRYPOINT [ "/redis_entrypoint.bsh" ]

CMD [ "redis-server" ]