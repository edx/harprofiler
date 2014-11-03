#!/bin/bash
# bootstrap local development environment (debian/ubuntu)

sudo apt-get install -y default-jre firefox git python-virtualenv xvfb
wget https://s3-us-west-1.amazonaws.com/lightbody-bmp/browsermob-proxy-2.0-beta-9-bin.zip -O bmp.zip
unzip -o bmp.zip
rm bmp.zip
virtualenv env
source env/bin/activate
pip install -r requirements.txt
