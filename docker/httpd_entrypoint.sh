#!/usr/bin/env bash

set -eu

source /opt/vip/vip.bsh

groupadd user -g ${GROUP_ID} -o 
useradd -u ${USER_ID} -o --create-home --home-dir /home/user -g user user

if [ "$1" == "httpd" ]; then

  OPTIONS=(-DFOREGROUND -f /usr/local/apache2/conf/httpd.conf)

  if [ "${VIP_HTTPD_DEBUG_INDEXES}" == "1" ]; then
    OPTIONS+=(-Ddebug_indexes)
  fi

  if [ "${VIP_HTTPD_DEPLOY_ON_START}" == "1" ]; then
  gosu user ${VIP_DJANGO_PROJECT}/collect_static.bsh
  fi

  /usr/local/apache2/bin/httpd "${OPTIONS[@]}"
else
  exec gosu user "${@}"
fi