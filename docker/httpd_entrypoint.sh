#!/usr/bin/env bash

set -eu

groupadd user -g ${GROUP_ID} -o 
useradd -u ${USER_ID} -o --create-home --home-dir /home/user -g user user

OPTIONS=(-DFOREGROUND -f /usr/local/apache2/conf/httpd.conf)

if [ "${VIP_HTTPD_DEBUG_INDEXES}" == "1" ]; then
  OPTIONS+=(-Ddebug_indexes)
fi

if [ "${VIP_HTTPD_DEPLOY_ON_START}" == "1" ]; then
  ${VIP_DJANGO_PROJECT}/_deploy.bsh
fi

/usr/local/apache2/bin/httpd "${OPTIONS[@]}"