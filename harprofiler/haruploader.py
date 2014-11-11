#!/usr/bin/env python
"""
A basic python script for posting HAR files to a HarStorage server.
"""
import argparse
from collections import Counter
import logging
import os

import requests

logging.basicConfig(format="%(levelname)s [%(name)s] %(message)s")
log = logging.getLogger('haruploader')
log.setLevel(logging.INFO)


def save_file(filepath, url):
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

    If any other exception is raised, we will put the file in another folder.
    Not to be retried, assuming the cause in this case is a poorly formatted
    har file.
    """

    basename = os.path.basename(filepath)
    url = url + "/results/upload"
    headers = {
        "Content-type": "application/x-www-form-urlencoded",
        "Automated": "true",
    }

    try:
        with open(filepath) as f:
            files = {'file': f.read()}
            resp = requests.post(url, data=files, headers=headers)

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
        move_file(filepath, 'failed')
        return 1
    else:
        log.info("{}: Successful".format(basename))
        move_file(filepath, 'success')
        return 0


def move_file(filepath, dest):
    base_dir = os.path.dirname(filepath)

    dirs = {
        'failed': os.path.join(base_dir, 'failed_uploads'),
        'success': os.path.join(base_dir, 'completed_uploads')
    }

    if not os.path.isdir(dirs[dest]):
        os.makedirs(dirs[dest])

    dest = os.path.join(dirs[dest], os.path.basename(filepath))
    os.rename(filepath, dest)


def upload_hars(path, url):
    log.info("Uploading har files from {} to {}".format(path, url))
    path = os.path.realpath(path)
    results = Counter()

    if os.path.isfile(path):
        results.update([
            save_file(path, url)
        ])
    elif os.path.isdir(path):
        for f in os.listdir(path):
            if f.endswith('.har'):
                results.update([
                    save_file(os.path.join(path, f), url)
                ])
    else:
        raise Exception("Can't find file or directory {}".format(path))

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
        help=("Path to HAR file or directory containing har files",
              "to be uploaded to harstorage"
              )
    )
    parser.add_argument(
        '--url',
        default='http://localhost:5000',
        help="URL of harstorage instance (default: 'http://localhost:5000')"
    )
    args = parser.parse_args()
    upload_hars(args.harpath, args.url)


if __name__ == "__main__":
    main()
