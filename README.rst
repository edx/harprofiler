harprofiler
===========

*record HAR files for automated web pageloads*

----

About
-----

:code:`harprofiler` is a python package containing the :code:`harprofiler` and :code:`haruploader` modules. It is used for profiling web pageloads.  :code:`harprofiler` loads a given URL and saves JSON files in HAR (HTTP Archive) format.  The HAR format contains detailed performance data about the page loading.  It will load the page once uncached, and then again with it cached in the browser.  A HAR file for each pageload is saved, and optionally uploaded to a :code:`harstorage` instance.

Installation
------------

install system packages::

    $ sudo apt-get install -y default-jre firefox git python-virtualenv unzip xvfb

clone the harprofiler repo::

    $ git clone https://github.com/edx/harprofiler.git

download browsermob proxy into branch root::

    $ cd harprofiler
    $ wget https://s3-us-west-1.amazonaws.com/lightbody-bmp/browsermob-proxy-2.0-beta-9-bin.zip -O bmp.zip
    $ unzip bmp.zip

create a virtualenv and install Python dependencies::

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -e .

Configuration
-------------

:code:`harprofiler` uses a yaml configuration file.

example config::

    browsermob_dir: ./browsermob-proxy-2.0-beta-9
    har_dir: ./hars
    harstorage_url: http://localhost:5000
    run_cached: true
    urls:
    - https://www.edx.org
    - https://www.edx.org/course-search
    virtual_display: true
    virtual_display_size_x: 1024
    virtual_display_size_y: 768

Usage
-----

::

    $ harprofiler -c myconfig.yaml

* results are saved in timestamped .har files, within the directory specified in the config file.


haruploader
===========

The :code:`haruploader` module is used for sending har files to a :code:`harstorage` instance.

harstorage references:
    * `On google code <https://code.google.com/p/harstorage/w/list/>`_
    * `Original Github repository <https://github.com/pavel-paulau/harstorage>`_

run uploader as standalone script:
    * Args:
        Path to HAR file or directory containing har files to be uploaded.
    * Options:
       `--url`: URL of harstorage instance (default: 'http://localhost:5000')
    * Example:
        `haruploader /path/to/file.har --url http://127.0.0.1:8000`
    * For help text:
        `haruploader -h`

run uploader as part of harprofiler:
    Make sure that :code:`harstorage_url` is set in the config file, and :code:`harprofiler` will run the uploader after it creates the HARs. This will call the :code:`upload_hars` method, using as args the :code:`har_dir` and :code:`harstorage_url` settings provided in the configuration file. If :code:`harstorage_url` is not set, then the uploader will not run."

error handling:
    * If the requests lib raises an exception, we will leave the file in the folder to be retried later. The error will still be logged though. These exceptions include the following:

        * :code:`requests.exceptions.ConnectionError`
        * :code:`requests.exceptions.TooManyRedirects`
        * :code:`requests.exceptions.Timeout`
        * :code:`requests.exceptions.HTTPError`
        * :code:`requests.exceptions.URLRequired`

    * If any other exception is raised while trying to upload the file, the file will be put in another folder, not to be retried. In this case, we assume the cause is a poorly formatted HAR file. The destination folder is titled :code:`failed_uploads`, and will be automatically created as a subdirectory of the folder that the HAR file was originally located.
    * If the file is successfully uploaded, it will be moved to a folder titled :code:`completed_uploads`.  Again, this will be automatically created as a subdirectory of the folder that the HAR file was originally located.
