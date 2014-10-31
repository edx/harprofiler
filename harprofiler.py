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

import argparse
import json
import re
import sys
from timeit import default_timer

from browsermobproxy import Server
from pyvirtualdisplay import Display
from selenium import webdriver


BROWSERMOB = './browsermob-proxy-2.0-beta-9'

VIRTUAL_DISPLAY_SIZE = (1024, 768)


def slugify(text):
    pattern = re.compile(r'[^a-z0-9]+')
    slug = '-'.join(word for word in pattern.split(text.lower()) if word)
    return slug


def save_har(har_name, har):
    with open(har_name, 'w') as f:
        json.dump(har, f, indent=2, ensure_ascii=False)


def parse_cmd_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='URL of page to load')
    parser.add_argument(
        '-x', '--headless', action='store_true', help='use headless display'
    )
    args = parser.parse_args()
    if not args.url.lower().startswith('http'):
        raise ValueError('URL must start with "http" or "https"')
    return args


def create_har(url):
    print 'starting browsermob proxy'
    server = Server('{}/bin/browsermob-proxy'.format(BROWSERMOB))
    server.start()

    proxy = server.create_proxy()
    profile = webdriver.FirefoxProfile()
    profile.set_proxy(proxy.selenium_proxy())
    driver = webdriver.Firefox(firefox_profile=profile)

    url_slug = slugify(url)
    proxy.new_har(url_slug)

    print 'loading page: {}'.format(url)
    start_time = default_timer()
    driver.get(url)
    end_time = default_timer()
    elapsed_secs = end_time - start_time

    har_name = '{}-{}.har'.format(url_slug, start_time)
    print 'saving HAR file: {}'.format(har_name)
    save_har(har_name, proxy.har)

    driver.quit()

    print 'stopping browsermob proxy'
    server.stop()

    return elapsed_secs


def main():
    try:
        args = parse_cmd_args()
    except ValueError as e:
        print e.message
        sys.exit(1)

    if args.headless:
        display = Display(visible=0, size=VIRTUAL_DISPLAY_SIZE)
        display.start()

    elapsed_secs = create_har(args.url)

    if args.headless:
        display.stop()

    print 'load time for {!r} was {:.3f} secs'.format(args.url, elapsed_secs)


if __name__ == '__main__':
    main()
