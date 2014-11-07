#!/usr/bin/env python
#
# Copyright (c) 2014 edX.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#

import json
import re
import os
import time
import yaml
import argparse
import logging

from browsermobproxy import Server
from pyvirtualdisplay import Display
from selenium import webdriver
from haruploader import upload_hars

logging.basicConfig(format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger('harprofiler')
log.setLevel(logging.INFO)


def load_config(config_file='config.yaml'):
    config = yaml.load(file(config_file))
    return config


def slugify(text):
    pattern = re.compile(r'[^a-z0-9]+')
    slug = '-'.join(word for word in pattern.split(text.lower()) if word)
    return slug


def save_har(har_name, har_dir, har):
    har_path = os.path.join(har_dir, har_name)
    with open(har_path, 'w') as f:
        json.dump(har, f, indent=2, ensure_ascii=False)


def create_hars(urls, har_dir, browsermob_dir, run_cached):
    for url in urls:
        log.info('starting browsermob proxy')
        server = Server('{}/bin/browsermob-proxy'.format(browsermob_dir))
        server.start()

        proxy = server.create_proxy()
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(proxy.selenium_proxy())
        driver = webdriver.Firefox(firefox_profile=profile)

        url_slug = slugify(url)
        proxy.new_har(url_slug)

        log.info('loading page: {}'.format(url))
        driver.get(url)

        har_name = '{}-{}.har'.format(url_slug, time.time())
        log.info('saving HAR file: {}'.format(har_name))
        save_har(har_name, har_dir, proxy.har)

        if run_cached:
            url_slug = '{}-cached'.format(slugify(url))
            proxy.new_har(url_slug)

            log.info('loading cached page: {}'.format(url))
            driver.get(url)

            har_name = '{}-{}.har'.format(url_slug, time.time())
            log.info('saving HAR file: {}'.format(har_name))
            save_har(har_name, har_dir, proxy.har)

        driver.quit()

        log.info('stopping browsermob proxy')
        server.stop()


def main(config_file='config.yaml'):
    config = load_config(config_file)

    if config['virtual_display']:
        display = Display(visible=0, size=(
            config['virtual_display_size_x'],
            config['virtual_display_size_y']
        ))
        display.start()

    if not os.path.isdir(config['har_dir']):
        os.makedirs(config['har_dir'])

    create_hars(config['urls'], config['har_dir'], config['browsermob_dir'], config['run_cached'])

    if config.get('harstorage_url'):
        upload_hars(config['har_dir'], config['harstorage_url'])

    if config['virtual_display']:
        display.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='harprofiler.py')
    parser.add_argument(
        '--config',
        default = 'config.yaml', 
        help = "Path to configuration file (Default: config.yaml)"
    )
    args = parser.parse_args()

    main(args.config)
