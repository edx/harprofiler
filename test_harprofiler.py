#!/usr/bin/env python

import glob
import logging
import os
import re
import shutil
import unittest
import uuid
import urlparse

from httmock import urlmatch, HTTMock
import requests
import yaml

import harprofiler
import haruploader


# Override logging level for tests
loggers = [
    logging.getLogger('haruploader'),
    logging.getLogger('harprofiler'),
]

for log in loggers:
    log.setLevel(logging.WARNING)


class ProfilerTest(unittest.TestCase):

    def test_run_cached_property(self):
        url = 'https://www.edx.org/'
        config = yaml.load(file('test_config.yaml'))
        profiler = harprofiler.HarProfiler(config, url)
        self.assertTrue(profiler.run_cached)

    def test_label_prefix(self):
        url = 'https://www.edx.org/'
        expected_label = 'testprefix-https-www-edx-org'
        config = yaml.load(file('test_config.yaml'))
        profiler = harprofiler.HarProfiler(config, url)
        self.assertEqual(profiler.label, expected_label)

    def test_cached_label_prefix(self):
        url = 'https://www.edx.org/'
        expected_label = 'testprefix-https-www-edx-org-cached'
        config = yaml.load(file('test_config.yaml'))
        profiler = harprofiler.HarProfiler(config, url)
        self.assertEqual(profiler.cached_label, expected_label)

    def test_blank_label_prefix(self):
        url = 'https://www.edx.org/'
        expected_label = 'https-www-edx-org-cached'
        config = yaml.load(file('test_config.yaml'))
        config['label_prefix'] = None
        profiler = harprofiler.HarProfiler(config, url)
        self.assertEqual(profiler.cached_label, expected_label)

    def test_slugify_simple_url(self):
        url = 'https://www.edx.org/'
        expected_slug = 'https-www-edx-org'
        config = yaml.load(file('test_config.yaml'))
        profiler = harprofiler.HarProfiler(config, url)
        slug = profiler.slugify(url)
        self.assertEqual(slug, expected_slug)

    def test_slugify_complex_url(self):
        url = 'https://www.edx.org/course/mitx/foo-2881#.VE6swYWFuR9'
        expected_slug = 'https-www-edx-org-course-mitx-foo-2881-ve6swywfur9'
        config = yaml.load(file('test_config.yaml'))
        profiler = harprofiler.HarProfiler(config, url)
        slug = profiler.slugify(url)
        self.assertEqual(slug, expected_slug)

    def test_default_config(self):
        cfg = yaml.load(file('test_config.yaml'))
        self.assertEqual(
            cfg['browsermob_dir'],
            './browsermob-proxy-2.0-beta-9'
        )
        self.assertTrue(cfg['run_cached'])
        self.assertTrue(cfg['virtual_display'])
        self.assertEqual(cfg['virtual_display_size_x'], 1024)
        self.assertEqual(cfg['virtual_display_size_y'], 768)


class HarFileTestCase(unittest.TestCase):
    def setUp(self):
        self.config = yaml.load(file('test_config.yaml'))
        self.test_dir = self.config['har_dir']
        os.makedirs(self.test_dir)
        self.addCleanup(self.remove_hars)

    def remove_hars(self):
        shutil.rmtree(self.test_dir)


class AcceptanceTest(HarFileTestCase):
    def test_main(self):
        harprofiler.main('test_config.yaml')
        num_urls = len(self.config['urls'])
        num_pageloads = num_urls * 2  # uncached and cached
        num_hars = len(glob.glob(os.path.join(self.test_dir, '*.har')))
        self.assertEqual(num_hars, num_pageloads)


class StorageTest(HarFileTestCase):
    """
    Tests to confirm that the response handling for sending to harstorage works
    as expected.
    """
    def setUp(self):
        super(StorageTest, self).setUp()
        self.url = self.config['harstorage_url']
        self.test_file = os.path.join(
            self.test_dir, str(uuid.uuid4()) + '.har'
        )
        with open(self.test_file, 'w') as f:
            f.write("I'm a fake har file")

    def test_success(self):
        """
        If a file is successfully sent to harstorage, then it is put in
        the 'completed_uploads' folder.
        """
        @urlmatch(method='post')
        def harstorage_mock_success(*args, **kwargs):
            return {
                'status_code': 200,
                'content': 'Successful'
            }

        with HTTMock(harstorage_mock_success):
            haruploader.upload_hars(self.test_dir, self.url)

        expected_file = os.path.join(
            self.test_dir,
            'completed_uploads',
            os.path.basename(self.test_file)
        )

        self.assertTrue(os.path.isfile(expected_file))

    def test_failure_bad_file(self):
        """
        If a file fails to be sent to harstorage because it is malformed,
        then it is put in a folder of failed files so that we can possibly
        inspect them.
        """
        @urlmatch(method='post')
        def harstorage_mock_parsing_error(*args, **kwargs):
            return {
                'status_code': 200,
                'content': 'KeyError: timing'
            }

        with HTTMock(harstorage_mock_parsing_error):
            haruploader.upload_hars(self.test_dir, self.url)

        expected_file = os.path.join(
            self.test_dir,
            'failed_uploads',
            os.path.basename(self.test_file)
        )

        self.assertTrue(os.path.isfile(expected_file))

    def test_failure_bad_status(self):
        """
        If a file fails to be sent to harstorage because of a 500 error,
        then it is left in the folder to retry.
        """
        @urlmatch(method='post')
        def harstorage_mock_server_error(*args, **kwargs):
            return {
                'status_code': 500,
                'content': 'Internal Server Error',
            }

        with HTTMock(harstorage_mock_server_error):
            haruploader.upload_hars(self.test_dir, self.url)

        self.assertTrue(os.path.isfile(self.test_file))

    def test_failure_bad_connection(self):
        """
        If a file fails to be sent to harstorage because of a connection issue,
        then it is left in the folder to retry.
        """
        @urlmatch(method='post')
        def harstorage_mock_bad_connection(*args, **kwargs):
            raise requests.exceptions.ConnectionError('ConnectionError')

        with HTTMock(harstorage_mock_bad_connection):
            haruploader.upload_hars(self.test_dir, self.url)

        self.assertTrue(os.path.isfile(self.test_file))

    def test_failure_timeout(self):
        """
        If a file fails to be sent to harstorage because of a timeout,
        then it is left in the folder to retry.
        """
        @urlmatch(method='post')
        def harstorage_mock_timeout(*args, **kwargs):
            raise requests.exceptions.Timeout('TimeoutError')

        with HTTMock(harstorage_mock_timeout):
            haruploader.upload_hars(self.test_dir, self.url)

        self.assertTrue(os.path.isfile(self.test_file))


if __name__ == '__main__':
    unittest.main(verbosity=2)
