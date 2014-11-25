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
import textwrap
import time
import yaml

from browsermobproxy import Server
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

from haruploader import upload_hars


logging.basicConfig(format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger('harprofiler')
log.setLevel(logging.INFO)


class HarProfiler:

    def __init__(self, config, url, login_first=False):
        self.url = url
        self.login_first = login_first

        self.login_user = config.get('login_user')
        self.login_password = config.get('login_password')

        self.browsermob_dir = config['browsermob_dir']
        self.har_dir = config['har_dir']
        self.label_prefix = config['label_prefix'] or ''
        self.run_cached = config['run_cached']
        self.virtual_display = config['virtual_display']
        self.virtual_display_size_x = config['virtual_display_size_x']
        self.virtual_display_size_y = config['virtual_display_size_y']

        self.label = '{}{}'.format(self.label_prefix, self.slugify(url))
        self.cached_label = '{}-cached'.format(self.label)

        epoch = time.time()
        self.har_name = '{}-{}.har'.format(self.label, epoch)
        self.cached_har_name = '{}-{}.har'.format(self.cached_label, epoch)

    def __enter__(self):
        if self.virtual_display:
            log.info('starting virtual display')
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
        if self.virtual_display:
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

    def _login(self, driver):
        log.info('logging in...')

        error_msg = 'must specify login credentials in config'
        if self.login_user is None:
            raise RuntimeError(error_msg)
        if self.login_password is None:
            raise RuntimeError(error_msg)

        driver.get('https://courses.edx.org/login')

        # handle both old and new style logins
        try:
            email_field = driver.find_element_by_id('email')
            password_field = driver.find_element_by_id('password')
        except NoSuchElementException:
            email_field = driver.find_element_by_id('login-email')
            password_field = driver.find_element_by_id('login-password')
        email_field.send_keys(self.login_user)
        password_field.send_keys(self.login_password)
        password_field.submit()

    def _add_page_event_timings(self, driver, har):
        jscript = textwrap.dedent("""
            var performance = window.performance || {};
            var timings = performance.timing || {};
            return timings;
            """)
        timings = driver.execute_script(jscript)
        har['log']['pages'][0]['pageTimings']['onContentLoad'] = (
            timings['domContentLoadedEventEnd'] - timings['navigationStart']
        )
        har['log']['pages'][0]['pageTimings']['onLoad'] = (
            timings['loadEventEnd'] - timings['navigationStart']
        )
        return har

    def load_page(self):
        try:
            driver, proxy = self._make_proxied_webdriver()

            if self.login_first:
                self._login(driver)

            proxy.new_har(self.label)
            log.info('loading page: {}'.format(self.url))
            driver.get(self.url)
            har = self._add_page_event_timings(driver, proxy.har)
            self._save_har(har)

            if self.run_cached:
                proxy.new_har(self.cached_label)
                log.info('loading cached page: {}'.format(self.url))
                driver.get(self.url)
                har = self._add_page_event_timings(driver, proxy.har)
                self._save_har(har, cached=True)
        except Exception:
            raise
        finally:
            driver.quit()

    def slugify(self, text):
        pattern = re.compile(r'[^a-z0-9]+')
        slug = '-'.join(word for word in pattern.split(text.lower()) if word)
        return slug


def main(config_file='config.yaml'):
    config = yaml.load(file(config_file))

    for url_config in config['urls']:
        if isinstance(url_config, basestring):
            login_first = False
            url = url_config
        else:
            login_first = url_config[1]
            url = url_config[0]
        with HarProfiler(config, url, login_first) as profiler:
            profiler.load_page()

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
