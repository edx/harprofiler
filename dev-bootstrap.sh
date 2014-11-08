#!/bin/bash
# bootstrap local development environment (debian/ubuntu)

SYSTEM_PACKAGES=(default-jre firefox git python-virtualenv unzip xvfb)
BROWSERMOBPROXY_DIR=browsermob-proxy-2.0-beta-9
BROWSERMOBPROXY_DOWNLOAD_URL=https://s3-us-west-1.amazonaws.com/lightbody-bmp/$BROWSERMOBPROXY_DIR-bin.zip


# Check each system package requirement and install if needed
for package in ${SYSTEM_PACKAGES[@]}; do
    dpkg -s $package 2>/dev/null >/dev/null || sudo apt-get -y install $package
done

# Download and unzip browsermob-proxy server if it doesn't exist
if [ ! -d "$BROWSERMOBPROXY_DIR" ]; then
    wget $BROWSERMOBPROXY_DOWNLOAD_URL -O $BROWSERMOBPROXY_DIR-bin.zip
    unzip $BROWSERMOBPROXY_DIR-bin.zip
    rm $BROWSERMOBPROXY_DIR-bin.zip
fi

# Create virtualenv and install requirements
virtualenv env
source env/bin/activate
pip install -r requirements.txt
