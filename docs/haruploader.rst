===========
haruploader
===========

The :code:`haruploader` module is used for sending har files to a :code:`harstorage` instance.

harstorage references:

* `On google code <https://code.google.com/p/harstorage/w/list/>`_
* `Original Github repository <https://github.com/pavel-paulau/harstorage>`_

------------------------------------
Run haruploader as standalone script
------------------------------------

* Args:
    Path to HAR file or directory containing har files to be uploaded.
* Options:
    :code:`--url`: URL of harstorage instance (default: 'http://localhost:5000')
* Example:
    :code:`python haruploader.py /path/to/HAR/file.har --url http://127.0.0.1:8000`
* For help text:
    :code:`python haruploader.py -h`

-----------------------------------
Run uploader as part of harprofiler
-----------------------------------

Make sure that `harstorage_url` is set in the config file, and :code:`harprofiler` will run the uploader after it creates the HARs. This will call the :code:`upload_hars` method, using as args the :code:`har_dir` and :code:`harstorage_url` settings provided in the configuration file.

--------------
Error handling
--------------

* If the requests lib raises an exception, we will leave the file in the folder to be retried later. The error will still be logged though. These exceptions include the following::

    requests.exceptions.ConnectionError
    requests.exceptions.TooManyRedirects
    requests.exceptions.Timeout
    requests.exceptions.HTTPError
    requests.exceptions.URLRequired

* If any other exception is raised while trying to upload the file, the file will be put in another folder, not to be retried. In this case, we assume the cause is a poorly formatted HAR file. The destination folder is titled :code:`failed_uploads`, and will be automatically created as a subdirectory of the folder that the HAR file was originally located.

* If the file is successfully uploaded, it will be moved to a folder titled :code:`completed_uploads`.  Again, this will be automatically created as a subdirectory of the folder that the HAR file was originally located.
