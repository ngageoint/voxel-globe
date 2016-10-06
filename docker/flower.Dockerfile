FROM python

ADD requirements_flower_derived.txt /

RUN pip install -r /requirements_flower_derived.txt && \
    rm -rf ~/.cache

ARG GOSU_VERSION=1.9
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y curl ca-certificates && \
    curl -Lo /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" && \
    curl -Lo /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" && \
    export GNUPGHOME="$(mktemp -d)" && \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 && \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu && \
    rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc && \
    chmod +x /usr/local/bin/gosu && \
    gosu nobody true && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

ADD flower_endpoint.bsh /

ENV USER_ID=1000 GROUP_ID=1000

CMD ["/flower_endpoint.bsh"]