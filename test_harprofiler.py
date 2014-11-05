#!/usr/bin/env python

import glob
import os
import unittest

import harprofiler


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


if __name__ == '__main__':
    unittest.main(verbosity=2)
