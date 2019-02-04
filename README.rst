[ARCHIVED] harprofiler
===========================================
This repository has been archived and is no longer supported—use it at your own risk. This repository may depend on out-of-date libraries with security issues, and security updates will not be provided. Pull requests against this repository will also not be merged.

Overview
===========

*record har files for automated web pageloads*

.. image:: https://travis-ci.org/edx/harprofiler.svg?branch=master
    :target: https://travis-ci.org/edx/harprofiler

----

About
-----

`harprofiler` is a python utility used for profiling web pageloads.  It loads web pages and saves JSON files in HAR (HTTP Archive) format.  By default, it will load a page once uncached, and then again with it cached in the browser.  A HAR file for each pageload is saved locally, and optionally uploaded to a HARStorage server instance. HAR files contain a log of HTTP client/server conversation and can be used for analysis of page load performance.

Documentation
-------------

Please visit: `harprofiler.readthedocs.org <http://harprofiler.readthedocs.org>`_
