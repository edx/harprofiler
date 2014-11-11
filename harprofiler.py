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

import argparse
import json
import logging
import os
import re
import time
import yaml

from browsermobproxy import Server
from pyvirtualdisplay import Display
from selenium import webdriver

from haruploader import upload_hars


logging.basicConfig(format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger('harprofiler')
log.setLevel(logging.INFO)


class HarProfiler:

    def __init__(self, config, url):
        self.har_dir = config['har_dir']
        self.browsermob_dir = config['browsermob_dir']
        self.virtual_display = config['virtual_display']
        self.virtual_display_size_x = config['virtual_display_size_x']
        self.virtual_display_size_y = config['virtual_display_size_y']

        self.url_slug = self.slugify(url)
        self.cached_url_slug = '{}-cached'.format(self.url_slug)

        epoch = time.time()
        self.har_name = '{}-{}.har'.format(self.url_slug, epoch)
        self.cached_har_name = '{}-{}.har'.format(self.cached_url_slug, epoch)

    def __enter__(self):
        log.info('starting virtual display')
        if self.virtual_display:
            self.display = Display(visible=0, size=(
                self.virtual_display_size_x,
                self.virtual_display_size_y
            ))
            self.display.start()

        log.info('starting browsermob proxy')
        self.server = Server('{}/bin/browsermob-proxy'.format(
            self.browsermob_dir)
        )
        self.server.start()
        return self

    def __exit__(self, type, value, traceback):
        log.info('stopping browsermob proxy')
        self.server.stop()
        log.info('stopping virtual display')
        self.display.stop()

    def _make_proxied_webdriver(self):
        proxy = self.server.create_proxy()
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(proxy.selenium_proxy())
        driver = webdriver.Firefox(firefox_profile=profile)
        return (driver, proxy)

    def _save_har(self, har, cached=False):
        if not os.path.isdir(self.har_dir):
            os.makedirs(self.har_dir)
        if not cached:
            har_name = self.har_name
        elif cached:
            har_name = self.cached_har_name

        log.info('saving HAR file: {}'.format(har_name))
        with open(os.path.join(self.har_dir, har_name), 'w' ) as f:
            json.dump(har, f, indent=2, ensure_ascii=False)

    def load_page(self, url, run_cached=True):
        driver, proxy = self._make_proxied_webdriver()
        proxy.new_har(self.url_slug)
        log.info('loading page: {}'.format(url))
        driver.get(url)
        self._save_har(proxy.har)

        if run_cached:
            proxy.new_har(self.cached_url_slug)
            log.info('loading cached page: {}'.format(url))
            driver.get(url)
            self._save_har(proxy.har, cached=True)

        driver.quit()

    def slugify(self, text):
        pattern = re.compile(r'[^a-z0-9]+')
        slug = '-'.join(word for word in pattern.split(text.lower()) if word)
        return slug


def main(config_file='config.yaml'):
    config = yaml.load(file(config_file))

    for url in config['urls']:
        with HarProfiler(config, url) as profiler:
            profiler.load_page(url)

    if config.get('harstorage_url'):
        upload_hars(config['har_dir'], config['harstorage_url'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='harprofiler.py')
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to configuration file (Default: config.yaml)'
    )
    args = parser.parse_args()

    main(args.config)
