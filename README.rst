=============================
Apache Atlas Client in Python
=============================


.. image:: https://img.shields.io/pypi/v/atlasclient.svg
        :target: https://pypi.python.org/pypi/atlasclient

.. image:: https://img.shields.io/travis/jpoullet2000/atlasclient.svg
        :target: https://travis-ci.org/jpoullet2000/atlasclient

.. image:: https://coveralls.io/repos/github/jpoullet2000/atlasclient/badge.svg?branch=master
        :target: https://coveralls.io/github/jpoullet2000/atlasclient?branch=master

.. image:: https://readthedocs.org/projects/atlasclient/badge/?version=latest
        :target: https://atlasclient.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/jpoullet2000/atlasclient/shield.svg
     :target: https://pyup.io/repos/github/jpoullet2000/atlasclient/
     :alt: Updates


Apache Atlas client in Python. 
Only compatible with Apache Atlas REST API **v2**. 

* Free software: Apache Software License 2.0
* Documentation: https://atlasclient.readthedocs.io.

Get started
-----------

    >>> from atlasclient.client import Atlas
    >>> client = Atlas('<atlas.host>', port=21000, username='admin', password='admin')
    >>> client.entityguid(<guid>).status
    >>> params = {'attrName': 'name', 'attrValue': 'data', 'offset': '1', 'limit':'10'} 
    >>> search_results = client.search_attribute(**params) 
    >>> for s in search_results:
    ...    for e in s.entities:
    ...         print(e.name)
    ...         print(e.guid)


Features
--------

* Lazy loading: requests are only performed when data are required and not yet available
* Resource object relationships: REST API from sub-resources are done transparently for the user, for instance the user does not have to know that it needs to trigger a different REST request for getting the classifications of a specific entity.  

TODO features  
-------------

* allow multiprocessing

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

