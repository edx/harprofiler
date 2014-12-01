===========
harprofiler
===========

------------
Installation
------------

Install via script (Ubuntu/Debian only)
---------------------------------------

Best method for getting up and running quickly. This will install the requirements and activate a virtualenv::

    $ source dev-bootstrap.sh

----

Manual install
--------------

System Requirements
+++++++++++++++++++

* Java JRE
* Firefox browser
* Python & Virtualenv
* `Browsermob proxy <http://bmp.lightbody.net/>`_

Python Requirements
+++++++++++++++++++

create a virtualenv and install Python dependencies::

    $ virtualenv env
    $ source env/bin/activate
    $ pip install -r requirements.txt

----

-------------
Configuration
-------------

`harprofiler` uses a yaml configuration file named `config.yaml`.

example config::

    browsermob_dir: ./browsermob-proxy-2.0-beta-9
    har_dir: ./hars
    harstorage_url: http://localhost:5000
    label_prefix:
    run_cached: true
    urls:
    - https://www.edx.org
    - https://www.edx.org/course-search
    virtual_display: true
    virtual_display_size_x: 1024
    virtual_display_size_y: 768

----

-----
Usage
-----

run pageload profiler::

    $ python harprofiler.py

* results are saved in timestamped .har files
