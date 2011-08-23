.. Yourls Client documentation master file, created by
   sphinx-quickstart on Fri Jul 29 10:30:13 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

YOURLS Client
=========================================

This small library was created to provide an easy interface to YOURLS from
a python program.

Simple example of shortening a URL::

    import yourls.client

    c = yourls.client.YourlsClient('http://localhost/yourls/yourls-api.php', username='username', password='password')
    url = c.shorten('http://autoqa.fedorahosted.org/autoqa', custom='autoqa')

Code Download
-------------
The code can be checked out from the github repository:
  * ``git clone git://github.com/tflink/python-yourls.git``

Or the code can be downloaded as a tarball from github:
  * https://github.com/downloads/tflink/python-yourls/python-yourls-0.1.1.tar.gz
API Documentation
-----------------
.. automodule:: client
    :members:

.. autoclass:: YourlsClient
   :members:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

