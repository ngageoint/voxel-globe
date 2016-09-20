FROM ubuntu:14.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        python python-wxgtk2.8 curl ca-certificates && \
    #Install pip
    curl -LO https://bootstrap.pypa.io/get-pip.py && \
    python get-pip.py && \
    rm get-pip.py && \
    pip install https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/winpdb/winpdb-1.4.8.tar.gz && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/*

ARG GOSU_VERSION=1.9
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y curl && \
    curl -Lo /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" && \
    curl -Lo /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" && \
    export GNUPGHOME="$(mktemp -d)" && \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu && \
    rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu && \
    gosu nobody true && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove curl && \
    rm -rf /var/lib/apt/lists/*

ENV USER_ID=1000 GROUP_ID=1000

ADD winpdb_entrypoint.bsh /

ENTRYPOINT ["/winpdb_entrypoint.bsh"]

CMD winpdb