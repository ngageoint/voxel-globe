FROM vsiri/sattel_voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

ADD requirements_uwsgi_derived.txt /

RUN apt-get update && \
    build_deps='python-dev gcc' && \
#Install packages
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        ${build_deps} && \
#install python packages
    pip install -r /requirements_uwsgi_derived.txt && \
#Remove build only deps, and clean up
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove \
        ${build_deps} && \
    rm -r /var/lib/apt/lists/* /root/.cache

ADD uwsgi_entrypoint.bsh /

ENTRYPOINT ["/tini", "--", "/uwsgi_entrypoint.bsh"]

STOPSIGNAL 3

CMD ["uwsgi"]