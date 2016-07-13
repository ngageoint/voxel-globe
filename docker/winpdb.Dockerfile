FROM ubuntu:16.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
    dpkg-dev build-essential swig python2.7-dev libwebkitgtk-dev libjpeg-dev \
    libtiff-dev checkinstall freeglut3 freeglut3-dev \
    libgtk2.0-dev  libsdl1.2-dev libgstreamer-plugins-base0.10-dev wget ca-certificates && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://sourceforge.net/projects/wxpython/files/wxPython/2.9.5.0/wxPython-src-2.9.5.0.tar.bz2 && \
    tar jxvf wxPython-src-2.9.5.0.tar.bz2

RUN cd /wxPython-src-2.9.5.0 && \
    ./configure --enable-stl && \
    CPPFLAGS=-std=c++11 make -j $(nproc) install
    cd wxPython && \
    CPPFLAGS=-std=c++11 python setup.py build && \
    python setup.py install
