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

