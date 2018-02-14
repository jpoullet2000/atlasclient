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

TO BE CONTINUED...


EntityREST
----------

This section explains how to create entities, update or delete them.  

Create Entity
~~~~~~~~~~~~~

To create an entity, one needs to create a Python dictionary which will define the entity. 
This can be done from a json file::
    
    import json 
    with open('my_entity_file.json') as json_file:
        entity_dict = json.load(json_file)

One can also just define the dictionary in Python. Note that if the user wants to pass a 'null' value, he should assign a value None in Python dictionary. It will be automatically convert to 'null' when requesting. 

Once the entity dictionary is created, the entity can actually be created on Atlas with::

    entity_post_collection = client.entity_post(data=entity_dict)
    for e in entity_post_collection:
        e.create()


Get entity by GUID
~~~~~~~~~~~~~~~~~~

If you know the GUID of the entity you want to fetch, you can follow these steps to get all info about this entity::
    
    entity = client.entity_guid(GUID)
    entity._data

To access some specific attribute of that entity, say the description::

    entity.entity['attributes']['description']

Update entity by GUID
~~~~~~~~~~~~~~~~~~~~~

Suppose you want to change the description of the entity here above and send it to Atlas::

    entity.entity['attributes']['description'] = 'my new description'
    entity.update(attribute='description')


Delete entity by GUID
~~~~~~~~~~~~~~~~~~~~~

To delete our entity::

    entity.delete()

TO BE CONTINUED...

LineageREST
-----------

TO BE DONE...

RelationshipREST
----------------

TO BE DONE...

TypesREST
---------

TO BE DONE...
