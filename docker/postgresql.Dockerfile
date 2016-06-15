FROM postgres:9.4.2

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

RUN apt-get update && \
    apt-get install --no-install-recommends -y postgresql-9.4-postgis-2.2 &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

#ADD http://download.osgeo.org/proj/vdatum/egm96_15/egm96_15.gtx /usr/share/proj
COPY egm96_15.gtx /usr/share/proj

EXPOSE 5432

COPY 00_init_postgis.sh /docker-entrypoint-initdb.d/
