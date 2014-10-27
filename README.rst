harprofiler
===========

*record har files for automated web pageloads*

----

About
-----

`harprofiler` is a python utility used for profiling web pageloads.  It loads a given URL and saves a JSON file in HAR (HTTP Archive) format.  The HAR format contains detailed performance data about the page loading.

----

Prerequisites
-------------

* Java JRE
* Python 2.7
* Firefox Browser

Installation
------------

install java runtime::

    $ sudo apt-get install default-jre

grab the profiler branch::

    $ git clone https://github.com/cgoldberg/harprofiler.git

download browsermob proxy into branch root::

    $ cd harprofiler
    $ curl https://s3-us-west-1.amazonaws.com/lightbody-bmp/browsermob-proxy-2.0-beta-9-bin.zip -o bmp.zip
    $ unzip bmp.zip

create a virtualenv and install deps::

    $ virtualenv env
    $ source env/bin/activate
    $ pip install selenium
    $ pip install browsermob-proxy

----

Usage
------

run pageload profiler::

    $ python harprofiler.py https://www.edx.org

(results are saved in timestamped har files)
