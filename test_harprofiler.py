#!/usr/bin/env python

import glob
import os
import unittest
import harprofiler
import haruploader
import uuid
import shutil
import os
import requests
import logging 
from httmock import urlmatch, HTTMock

# Override logging level for tests
log = logging.getLogger('haruploader')
log.setLevel(logging.WARNING)


class ProfilerTest(unittest.TestCase):

    def test_slugify_simple_url(self):
        url = 'https://www.edx.org/'
        expected_slug = 'https-www-edx-org'
        slug = harprofiler.slugify(url)
        self.assertEqual(slug, expected_slug)

    def test_slugify_complex_url(self):
        url = 'https://www.edx.org/course/mitx/foo-2881#.VE6swYWFuR9'
        expected_slug = 'https-www-edx-org-course-mitx-foo-2881-ve6swywfur9'
        slug = harprofiler.slugify(url)
        self.assertEqual(slug, expected_slug)

    def test_default_config(self):
        cfg = harprofiler.load_config(config_file='config.yaml')
        self.assertEqual(
            cfg['browsermob_dir'],
            './browsermob-proxy-2.0-beta-9'
        )
        self.assertTrue(cfg['run_cached'])
        self.assertTrue(cfg['virtual_display'])
        self.assertEqual(cfg['virtual_display_size_x'], 1024)
        self.assertEqual(cfg['virtual_display_size_y'], 768)


class AcceptanceTest(unittest.TestCase):

    def remove_hars(self):
        for f in glob.glob('*.har'):
            os.remove(f)

    def test_main(self):
        self.addCleanup(self.remove_hars)
        harprofiler.main()
        num_urls = len(harprofiler.load_config()['urls'])
        num_pageloads = num_urls * 2  # uncached and cached
        num_hars = len(glob.glob('*.har'))
        self.assertEqual(num_hars, num_pageloads)



class StorageTest(unittest.TestCase):
    """
    Tests to confirm that the response handling for sending to harstorage works
    as expected.
    """
    def setUp(self):
        self.test_dir = 'test-files-' + str(uuid.uuid4())
        os.makedirs(self.test_dir)

        self.test_file = os.path.join(self.test_dir, 'test-file.har')
        with open(self.test_file, 'w') as f:
            f.write("I'm a fake har file")

        self.url = "http://mockharstorage.com"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_success(self):
        """
        If a file is successfully sent to harstorage, then it is put in
        the 'completed_uploads' folder.
        """
        @urlmatch(method='post', netloc=r'(.*\.)?mockharstorage\.com$')
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
        @urlmatch(method='post', netloc=r'(.*\.)?mockharstorage\.com$')
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
        @urlmatch(method='post', netloc=r'(.*\.)?mockharstorage\.com$')
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
        @urlmatch(method='post', netloc=r'(.*\.)?mockharstorage\.com$')
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
        @urlmatch(method='post', netloc=r'(.*\.)?mockharstorage\.com$')
        def harstorage_mock_timeout(*args, **kwargs):
            raise requests.exceptions.Timeout('TimeoutError')

        with HTTMock(harstorage_mock_timeout):
            haruploader.upload_hars(self.test_dir, self.url)

        self.assertTrue(os.path.isfile(self.test_file))


if __name__ == '__main__':
    unittest.main(verbosity=2)
