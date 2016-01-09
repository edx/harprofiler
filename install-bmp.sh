#!/bin/bash

https://github.com/lightbody/browsermob-proxy/releases/download/

BROWSERMOBPROXY_DIR=browsermob-proxy-2.1.0-beta-4
BROWSERMOBPROXY_ZIP=${BROWSERMOBPROXY_DIR}-bin.zip
BROWSERMOBPROXY_DOWNLOAD_URL=https://github.com/lightbody/browsermob-proxy/releases/download/${BROWSERMOBPROXY_DIR}/$BROWSERMOBPROXY_ZIP

# Download and unzip browsermob-proxy server if it doesn't exist
if [ ! -d "$BROWSERMOBPROXY_DIR" ]; then
    wget $BROWSERMOBPROXY_DOWNLOAD_URL -O $BROWSERMOBPROXY_ZIP
    unzip $BROWSERMOBPROXY_ZIP
    rm $BROWSERMOBPROXY_ZIP
fi
