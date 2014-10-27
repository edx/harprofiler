#!/usr/bin/env python

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

    # TODO : add more tests


if __name__ == '__main__':
    unittest.main()
