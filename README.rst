harprofiler
===========

*record har files for automated web pageloads*

----

About
-----

`harprofiler` is a python utility used for profiling web pageloads.  It loads a given URL and saves JSON files in HAR (HTTP Archive) format.  The HAR format contains detailed performance data about the page loading.  It will load the page once uncached, and then again with it cached in the browser.  A HAR file for each pageload is saved.

Installation
------------

install system packages::

    $ sudo apt-get install -y default-jre firefox git python-virtualenv xvfb

clone the harprofiler repo::

    $ git clone https://github.com/cgoldberg/harprofiler.git

download browsermob proxy into branch root::

    $ cd harprofiler
    $ wget https://s3-us-west-1.amazonaws.com/lightbody-bmp/browsermob-proxy-2.0-beta-9-bin.zip -O bmp.zip
    $ unzip bmp.zip

create a virtualenv and install Python dependencies::

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r requirements.txt

Configuration
-------------

`harprofiler` uses a yaml configuration file named `config.yaml`.

example config::

    browsermob_dir: ./browsermob-proxy-2.0-beta-9
    run_cached: true
    urls:
    - https://www.edx.org
    - https://www.edx.org/course-search
    virtual_display: true
    virtual_display_size_x: 1024
    virtual_display_size_y: 768

Usage
-----

run pageload profiler::

    $ python harprofiler.py

* results are saved in timestamped .har files
