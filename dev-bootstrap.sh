#!/bin/bash
# bootstrap local development environment (debian/ubuntu)

SYSTEM_PACKAGES=(default-jre firefox git python-virtualenv unzip xvfb)

# Check each system package requirement and install if needed
sudo apt-get -qq -y update
for package in ${SYSTEM_PACKAGES[@]}; do
    dpkg -s $package 2>/dev/null >/dev/null || sudo apt-get -y install $package
done

bash install-bmp.sh

# Create virtualenv and install requirements
virtualenv env
source env/bin/activate
pip install -r requirements.txt
