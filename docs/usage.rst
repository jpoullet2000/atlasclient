========
Usage
========

To use atlasclient::

	import atlasclient


This Python client is based on the `Apache Atlas REST API v2`_. 

.. _Apache Atlas REST API v2: https://atlas.apache.org/api/v2/index.html

The following groups of resources can be accessed: 

- DiscoveryREST
- EntityREST
- LineageREST
- RelationshipREST
- TypesREST

Below a few examples to access some of the resources. 

Make sure atlasclient is properly installed (see `here <installation.html>`__).
First you need to create a connection object:: 

     from atlasclient.client import Atlas
     client = Atlas(your_atlas_host, port=21000, username='admin', password='admin')

Replace `your_atlas_host` by the actual host name of the Atlas server. Note that port 21000 might also be different in your case. Port 21000 is default port when using HTTP with Atlas, and 21443 for HTTPS. 


DiscoveryREST
-------------

This section explains how you can search for entities per attribute name, or search using a SQL-like query, and more ;). 

To search for entities with a special attribute name::

   params = {'attrName': 'name', 'attrValue': 'data', 'offset': '1', 'limit':'10'} 
   search_results = client.search_attribute(**params) 
   #  Info about all entities in one dict
   for s in search_results:
       print(s._data)
   #  Getting name and guid of each entity 
   for s in search_results:
       for e in s.entities:
           print(e.name)
           print(e.guid)


EntityREST
----------

TO BE DONE...

LineageREST
-----------

TO BE DONE...

RelationshipREST
----------------

TO BE DONE...

TypesREST
---------

TO BE DONE...
