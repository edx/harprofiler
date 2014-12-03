#!/usr/bin/env python

"""
Send HAR files to a HarStorage server via HTTP POST.
"""

import argparse
from collections import Counter
import logging
import os
import urlparse

import requests

logging.basicConfig(format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger('haruploader')
log.setLevel(logging.INFO)


class Uploader:

    def __init__(self, path, url):
        self.path = os.path.realpath(path)
        self.url = urlparse.urljoin(url, '/results/upload')

    def _save_file(self, filepath):
        """
        Sends the request to harstorage for the given path to a har file.

        If the requests lib raises an exception, we will leave the file in
        the folder to be retried later. The error will still be logged though.
        These exceptions include:
            * requests.exceptions.ConnectionError
            * requests.exceptions.TooManyRedirects
            * requests.exceptions.Timeout
            * requests.exceptions.HTTPError
            * requests.exceptions.URLRequired

        If any other exception is raised, we will put the file in another
        folder.  It will not be retried, assuming the cause in this case is a
        poorly formatted har file.
        """

        basename = os.path.basename(filepath)
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "Automated": "true",
        }

        try:
            with open(filepath) as f:
                data = {'file': f.read()}
                resp = requests.post(self.url, data=data, headers=headers)

                # Raise exception if 4XX or 5XX response code is returned
                # The exception raised here will be a subclass or instance
                # of requests.exceptions.RequestException.
                resp.raise_for_status()

                # Raise exception if response code is OK but response
                # text doesn't indicate success. This seems to happen
                # when the file isn't formatted exactly as expected.
                # e.g. 'KeyError: timings'
                if resp.text != 'Successful':
                    raise Exception(resp.text)
        except requests.exceptions.RequestException as e:
            log.info("{}: {}".format(basename, e.message))
            return 2
        except Exception as e:
            log.info("{}: {}".format(basename, e.message))
            self._move_file(filepath, 'failed')
            return 1
        else:
            log.info("{}: Successful".format(basename))
            self._move_file(filepath, 'success')
            return 0

    def _move_file(self, filepath, dest):
        base_dir = os.path.dirname(filepath)

        dirs = {
            'failed': os.path.join(base_dir, 'failed_uploads'),
            'success': os.path.join(base_dir, 'completed_uploads')
        }

        if not os.path.isdir(dirs[dest]):
            os.makedirs(dirs[dest])

        dest = os.path.join(dirs[dest], os.path.basename(filepath))
        os.rename(filepath, dest)

    def upload_hars(self):
        log.info(
            "Uploading har files from {} to {}".format(self.path, self.url)
        )
        results = Counter()

        if os.path.isfile(self.path):
            results.update([
                self._save_file(self.path, self.url)
            ])
        elif os.path.isdir(self.path):
            for f in os.listdir(self.path):
                if f.endswith('.har'):
                    results.update([
                        self._save_file(os.path.join(self.path, f))
                    ])
        else:
            raise Exception(
                "Can't find file or directory {}".format(self.path)
            )

        log.info(
            'Done.'
            '\n{} files successfully uploaded.'
            '\n{} files failed to upload and will not be retried.'
            '\n{} files failed to upload and will be retried next run.'
            ''.format(results[0], results[1], results[2])
        )


def main():
    """
    Runs as standalone script, explicitly passed path to HAR files.

    Args:
        Path to HAR file or directory containing har files to be uploaded.

    Options:
        --url = URL of harstorage instance (default: 'http://localhost:5000')

    Example:
        python haruploader.py /path/to/HAR/file.har --url http://127.0.0.1:8000

    For help text:
        python haruploader.py -h
    """
    parser = argparse.ArgumentParser(prog='haruploader.py')
    parser.add_argument(
        'harpath',
        help=("Path to HAR file or directory containing har files"
              "to be uploaded to harstorage"
              )
    )
    parser.add_argument(
        '--url',
        default='http://localhost:5000',
        help="URL of harstorage instance (default: 'http://localhost:5000')"
    )
    args = parser.parse_args()

    uploader = Uploader(args.harpath, args.url)
    uploader.upload_hars()


if __name__ == "__main__":
    main()
