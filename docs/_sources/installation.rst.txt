Installation
------------

Requirements
^^^^^^^^^^^^

MTCFeatures is a Python 3 module. Python 2 is not supported.

The `requests <http://docs.python-requests.org/en/master/>`_ module should be installed::

	$ pip install requests


Installation from PyPI
^^^^^^^^^^^^^^^^^^^^^^

The easiest way to install MTCFeatures is using pip::

	$ pip install MTCFeatures

Next, you need to install the data (see below).

Installation from source
^^^^^^^^^^^^^^^^^^^^^^^^

Download the latest release from github and run the included setup.py script:

* Visit https://github.com/pvankranenburg/MTCFeatures/releases
* Download the latest release
* In a command shell run the included setup.py script::

	$ cd /path/to/MTCFeatures
	$ python setup.py install

Next, you need to install the data (see below).

Install the data
^^^^^^^^^^^^^^^^

After installing the module, the datafiles need to be installed separately. Execute the following code in Python.

.. code-block:: python

	from MTCFeatures import downloadData
	downloadData(dest='user')

This will install the data files in a platform specific data directory in user space.
If you want the data files in a system wide directory, which would make the data available to all users, use dest='system'. Make sure
you have write permissions in the system wide data directory.

Data only
^^^^^^^^^

If you only want to use the data, visit the data repository at Zenodo: https://zenodo.org/record/3551003