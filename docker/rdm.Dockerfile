FROM ubuntu:14.04

ENV PATH=/opt/qt56/bin:$PATH \
    PKG_CONFIG_PATH=/opt/qt56/lib/pkgconfig \
    LD_LIBRARY_PATH=/opt/qt56/lib/x86_64-linux-gnu:/opt/qt56/lib
ENV REDIS_DESKTOP_MANAGER_VERSION=0.8.8
RUN build_deps="automake libtool libssl-dev libssh2-1-dev g++ libgl1-mesa-dev cmake ca-certificates make git" && \
    echo "deb http://ppa.launchpad.net/beineri/opt-qt561-trusty/ubuntu trusty main" > /etc/apt/sources.list.d/opt-qt561-trusty.list && \
    apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys C65D51784EDC19A871DBDBB710C56D0DE9977759 && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ${build_deps} \
        libssh2-1 qt56base qt56imageformats qt56tools qt56declarative qt56quickcontrols \
        libgl1-mesa-glx libgl1-mesa-dri && \
    git clone --recursive https://github.com/uglide/RedisDesktopManager.git -b ${REDIS_DESKTOP_MANAGER_VERSION} /rdm && \
    cd /rdm/src && \
    ./configure && \
    cd /rdm/src && \
    qmake && \
    make && \
    make install && \
    cd /usr/share/redis-desktop-manager/bin && \
    mv qt.conf qt.backup && \
    rm -rf /rdm && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove ${build_deps} && \
    rm -rf /var/lib/apt/lists/*

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

ENV USER_ID=1000 GROUP_ID=1000

LABEL com.nvidia.volumes.needed="nvidia_driver"

RUN echo "/usr/local/nvidia/lib" >> /etc/ld.so.conf.d/nvidia.conf && \
    echo "/usr/local/nvidia/lib64" >> /etc/ld.so.conf.d/nvidia.conf

ENV PATH /usr/local/nvidia/bin:${PATH}

LABEL dustify.runargs="-v /tmp/.X11-unix:/tmp/.X11-unix \
                       -e DISPLAY \
                       -e USER_ID=%DUSTIFY_USER_ID% \
                       -e GROUP_ID=%DUSTIFY_GROUP_ID%"

CMD groupadd user -g ${GROUP_ID} -o && \
    useradd -u ${USER_ID} -o --create-home --home-dir /home/user -g user user && \
    ldconfig && \
    LD_LIBRARY_PATH=/opt/qt56/lib gosu user /usr/share/redis-desktop-manager/bin/rdm
