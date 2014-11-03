harprofiler
===========

*record har files for automated web pageloads*

----

About
-----

`harprofiler` is a python utility used for profiling web pageloads.  It loads a given URL and saves JSON files in HAR (HTTP Archive) format.  The HAR format contains detailed performance data about the page loading.  It will load the page once uncached, and then again with it cached in the browser.  A HAR file for each pageload is saved.

Prerequisites
-------------

* Java JRE
* Python 2.7
* Firefox Browser

Installation
------------

install Java runtime and Xvfb::

    $ sudo apt-get install default-jre xvfb

grab the profiler branch::

    $ git clone https://github.com/cgoldberg/harprofiler.git

download browsermob proxy into branch root::

    $ cd harprofiler
    $ wget https://s3-us-west-1.amazonaws.com/lightbody-bmp/browsermob-proxy-2.0-beta-9-bin.zip -o bmp.zip
    $ unzip bmp.zip

create a virtualenv and install Python dependencies::

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r requirements.txt


Usage
-----

::

    $ python harprofiler.py -h
    usage: harprofiler.py [-h] [-x] url

    positional arguments:
      url             URL of page to load

    optional arguments:
      -h, --help      show this help message and exit
      -x, --headless  use headless display

Example
-------

run pageload profiler::

    $ python harprofiler.py https://www.edx.org

* results are saved in timestamped har files
