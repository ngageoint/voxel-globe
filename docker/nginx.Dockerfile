FROM vsiri/sattel_voxel_globe:common

MAINTAINER Andrew Neff <andrew.neff@visionsystemsinc.com>

ENV NGINX_VERSION 1.11.3-1~jessie
RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 && \
    echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list && \
    apt-get update && \
    apt-get install --no-install-recommends --no-install-suggests -y \
            ca-certificates \
            nginx=${NGINX_VERSION} \
            cron \
            gettext-base && \
    rm -rf /var/lib/apt/lists/*

ADD requirements_nginx_derived.txt /

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends gcc python-dev libssl-dev libffi-dev && \
    pip install virtualenv && \
    virtualenv /opt/certbot && \
    . /opt/certbot/bin/activate && \
    pip install -r /requirements_nginx_derived.txt && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove gcc python-dev libssl-dev libffi-dev && \
    rm -r /var/lib/apt/lists/*

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl && \
    curl -sLo /usr/local/bin/ep https://github.com/kreuzwerker/envplate/releases/download/1.0.0-RC1/ep-linux && \
    chmod +x /usr/local/bin/ep && \
    DEBIAN_FRONTEND=noninteractive apt-get purge -y --auto-remove curl && \
    rm -r /var/lib/apt/lists/*

ADD nginx_entrypoint.bsh nginx_crontab.txt /

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log && \
    ln -sf /dev/stderr /var/log/nginx/error.log

ENTRYPOINT ["/tini", "--", "/nginx_entrypoint.bsh"]

CMD ["nginx"]