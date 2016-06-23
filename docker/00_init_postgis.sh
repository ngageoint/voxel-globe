#!/usr/bin/env bash

#A .sh file is the OLD way of doing things. In the newest postgres docker images,
#a .sql file can be used instead

gosu postgres pg_ctl -w start -o "-h localhost"

gosu postgres psql <<EOSQL
CREATE DATABASE template_postgis;
UPDATE pg_database SET datistemplate = TRUE WHERE datname = 'template_postgis';
\c template_postgis
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
CREATE EXTENSION fuzzystrmatch;
CREATE EXTENSION postgis_tiger_geocoder;
GRANT ALL ON geometry_columns TO PUBLIC;
GRANT ALL ON geography_columns TO PUBLIC;
GRANT ALL ON spatial_ref_sys TO PUBLIC;
EOSQL

gosu postgres pg_ctl -w stop