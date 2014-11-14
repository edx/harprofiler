#!/bin/bash

BROWSERMOBPROXY_DIR=browsermob-proxy-2.0-beta-9
BROWSERMOBPROXY_ZIP=$BROWSERMOBPROXY_DIR-bin.zip
BROWSERMOBPROXY_DOWNLOAD_URL=https://s3-us-west-1.amazonaws.com/lightbody-bmp/$BROWSERMOBPROXY_ZIP

# Download and unzip browsermob-proxy server if it doesn't exist
if [ ! -d "$BROWSERMOBPROXY_DIR" ]; then
    wget $BROWSERMOBPROXY_DOWNLOAD_URL -O $BROWSERMOBPROXY_ZIP
    unzip $BROWSERMOBPROXY_ZIP
    rm $BROWSERMOBPROXY_ZIP
fi
