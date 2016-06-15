#!/usr/bin/env bash

set -eu

OPTIONS=(-DFOREGROUND -f /usr/local/apache2/conf/httpd.conf)

if [ "${VIP_HTTPD_DEBUG_INDEXES}" == "1" ]; then
  OPTIONS+=(-Ddebug_indexes)
fi

/usr/local/apache2/bin/httpd "${OPTIONS[@]}"