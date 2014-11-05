#!/usr/bin/env python
#
# Corey Goldberg, 2014
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#

import json
import re
import time
import yaml

from browsermobproxy import Server
from pyvirtualdisplay import Display
from selenium import webdriver


def load_config(config_file='config.yaml'):
    config = yaml.load(file(config_file))
    return config


def slugify(text):
    pattern = re.compile(r'[^a-z0-9]+')
    slug = '-'.join(word for word in pattern.split(text.lower()) if word)
    return slug


def save_har(har_name, har):
    with open(har_name, 'w') as f:
        json.dump(har, f, indent=2, ensure_ascii=False)


def create_hars(urls, browsermob_dir, run_cached):
    for url in urls:
        print 'starting browsermob proxy'
        server = Server('{}/bin/browsermob-proxy'.format(browsermob_dir))
        server.start()

        proxy = server.create_proxy()
        profile = webdriver.FirefoxProfile()
        profile.set_proxy(proxy.selenium_proxy())
        driver = webdriver.Firefox(firefox_profile=profile)

        url_slug = slugify(url)
        proxy.new_har(url_slug)

        print 'loading page: {}'.format(url)
        driver.get(url)

        har_name = '{}-{}.har'.format(url_slug, time.time())
        print 'saving HAR file: {}'.format(har_name)
        save_har(har_name, proxy.har)

        if run_cached:
            url_slug = '{}-cached'.format(slugify(url))
            proxy.new_har(url_slug)

            print 'loading cached page: {}'.format(url)
            driver.get(url)

            har_name = '{}-{}.har'.format(url_slug, time.time())
            print 'saving HAR file: {}'.format(har_name)
            save_har(har_name, proxy.har)

        driver.quit()

        print 'stopping browsermob proxy'
        server.stop()


def main():
    config = load_config()

    if config['virtual_display']:
        display = Display(visible=0, size=(
            config['virtual_display_size_x'],
            config['virtual_display_size_y']
        ))
        display.start()

    create_hars(config['urls'], config['browsermob_dir'], config['run_cached'])

    if config['virtual_display']:
        display.stop()


if __name__ == '__main__':
    main()
