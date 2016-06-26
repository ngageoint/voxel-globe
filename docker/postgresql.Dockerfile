FROM postgres:9.4.2

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        postgresql-9.4-postgis-2.2 &&\
    rm -rf /var/lib/apt/lists/*

ADD http://download.osgeo.org/proj/vdatum/egm96_15/egm96_15.gtx /usr/share/proj

EXPOSE 5432

ENV USER_ID=999 \
    GROUP_ID=999

COPY 00_init_postgis.sh /docker-entrypoint-initdb.d/

ADD postgresql_entrypoint.bsh /

ENTRYPOINT ["/postgresql_entrypoint.bsh"]

CMD ["postgres"]