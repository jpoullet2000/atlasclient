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
- AdminREST

Below a few examples to access some of the resources. 

Make sure atlasclient is properly installed (see `here <installation.html>`__).

First you need to create a connection object:: 

    from atlasclient.client import Atlas
    client = Atlas(your_atlas_host, port=21000, username='admin', password='admin')

Replace `your_atlas_host` by the actual host name of the Atlas server. Note that port 21000 might also be different in your case. Port 21000 is default port when using HTTP with Atlas, and 21443 for HTTPS. 

To access the list of entry points::

    from atlasclient.client import ENTRY_POINTS
    ENTRY_POINTS

You'll get a dictionary with ('key': 'value') corresponding to ('client method': 'model class'): `{'entity_guid': <class 'atlasclient.models.EntityGuid'>, ...}`. 
For example, we can use::

    client.entity_guid(GUID)

'entity_guid' is used as a method of the 'client' object.


DiscoveryREST
-------------

This section explains how you can search for entities per attribute name, or search using a SQL-like query, and more ;). 


Search by attribute
~~~~~~~~~~~~~~~~~~~

To search for entities with a special attribute name::

    params = {'typeName': 'DataSet', 'attrName': 'name', 'attrValue': 'data', 'offset': '1', 'limit': '10'}
    search_results = client.search_attribute(**params) 
    #  Info about all entities in one dict
    for s in search_results:
        print(s._data)
    #  Getting name and guid of each entity 
    for s in search_results:
        for e in s.entities:
            print(e.name)
            print(e.guid)


Search with basic terms
~~~~~~~~~~~~~~~~~~~~~~~

To retrieve data for the specified full text query:: 

    params = {'attrName': 'name', 'attrValue': 'data', 'offset': '1', 'limit': '10'} 
    search_results = client.search_basic(**params)
    for s in search_results:
        for e in s.entities
            print(e.guid)

Attribute based search `(POST /v2/search/basic)` for entities satisfying the search parameters::

    data = {'attrName': 'name', 'attrValue': 'data', 'offset': '1', 'limit': '10'}
    search_results = client.search_basic.create(data=data)
    for e in search_results.entities:
        print(e.guid)


Search by DSL
~~~~~~~~~~~~~

To retrieve data for the specified DSL::

    params = {'typeName': 'hdfs_path', 'classification': 'Confidential'}
    search_results = client.search_dsl(**params)
    for s in search_results:
        for e in s.entities:
            print(e.classificationNames)
            print(e.attributes)


DSL Search has a helper function available when you specify a SELECT clause or attribute in your search query.

    _search_collection = client.search_dsl(**dsl_param)
    for collection in _search_collection:
        attributes = collection.flatten_attrs()

SavedSearchREST
----------

This section explains how to get, create saved search, update or delete them. 

Get all saved search for user
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve saved search for the Atlas user::

    search_saved = client.search_saved()
    for s in search_saved:
        print(s._data)
        print(s.name)


Get saved search by name (for user)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To retrieve saved search for the Atlas user by name::

    search_saved = client.search_saved(NAME)
    print(s.name)
    print(s.ownerName)


Create saved search by name (for user)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create saved search for the Atlas user by name::

    payload = """{
    "name": "trying",
    "ownerName": "svc_data_catalog_api",
    "searchType": "BASIC",
    "searchParameters": {
        "typeName": "rdbms_db",
        "excludeDeletedEntities": true,
        "includeClassificationAttributes": false,
        "includeSubTypes": true,
        "includeSubClassifications": true,
        "limit": 0,
        "offset": 0
    },
        "uiParameters": "Select::0,Name::1,Owner::2,Description::3,Type::4,Classifications::5,Term::6,Db::7"
    }"""

    response = client.search_saved.create(data=json.loads(payload))


Update saved search by guid (for user)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create saved search for the Atlas user by name::

    payload = """{"guid": "fa1f15f0-09fc-403d-8ad7-3bcac379c3f9", "name": "trying2"}"""
    response = client.search_saved.update(data=json.loads(payload))


To delete saved search by guid (for user)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To delete saved search for the Atlas user by guid::

    client.search_saved.delete(guid=GUID)


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

    client.entity_post.create(data=entity_dict)


Get entity by GUID
~~~~~~~~~~~~~~~~~~

If you know the GUID of the entity you want to fetch, you can follow these steps to get all info about this entity::
    
    entity = client.entity_guid(GUID)
    entity._data

To access some specific attribute of that entity, say the description::

    entity.entity['attributes']['description']

It shows up as a dictionary. So one can get the list of all attributes with::

    entity.entity['attributes'].keys()


Update entity by GUID
~~~~~~~~~~~~~~~~~~~~~

Suppose you want to change the description of the entity here above and send it to Atlas::

    entity.entity['attributes']['description'] = 'my new description'
    entity.update(attribute='description')


Delete entity by GUID
~~~~~~~~~~~~~~~~~~~~~

To delete our entity::

    entity.delete()


Get classifications by GUID
~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get all classification type names related to an entity GUID::

     entity = client.entity(GUID)
     for classification_info in entity.classifications:
         for classification_item in classification_info.list:
             print(classification_item.typeName)


Update classifications by GUID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To update classifications to an existing entity represented by a guid::

     entity = client.entity(GUID)
     for classification_info in entity.classifications:
         for classification_item in classification_info.list:
             if classification_item.typeName == 'Semi-Confidential'
                 classification_item.typeName = 'Confidential'
     entity.classifications.update()

The entity will now be tagged as 'Confidential' instead of 'Semi-Confidential'. 

     
Create classifications by GUID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To add classifications to an existing GUID:: 

   new_classifications = [{"typeName": "Confidential"},
	                  {"typeName": "Customer"}
                         ]
   entity = client.entity(GUID)
   entity.classifications.create(data=new_classifications)
 
This will create 2 new classifications for the entity.

Get classification info by GUID and by classification type name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get info about some specific classification for some entity::

    
     entity = client.entity(GUID)
     entity.classifications('Confidential').refresh()._data

The refresh() method is used to load data from the Atlas server, which is then stored in the _data attribute. 

To get some specific info about the classification, say the 'totalCount'::

    entity.classifications('Confidential').totalCount

In that case, no need to use the refresh method since the client will see that the attribute totalCount is not yet available and will therefore send a request to the Atlas server.


Delete a classification by GUID
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To delete a given classification from an existing entity represented by a GUID::

    client.entity_guid(GUID).classifications('Confidential').delete()

This will delete the classification 'Confidential' for that specific entity only.
 

Get entities by bulk
~~~~~~~~~~~~~~~~~~~~

To retrieve list of entities identified by its GUIDs::

    bulk_collection = client.entity_bulk(guid=[GUID1, GUID2])


Get entities by bulk (with relationship attributes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In some cases, you may want to need the details of relationship attributes along with entity,
There is a helper function available for that::

    bulk_collection = client.entity_bulk(guid=[GUID1, GUID2])
    for collection in bulk_collection:
        entities = collection.entities_with_relationships()


    # You can also specify the attributes as a list you want in particular to optimize implementation
    for collection in bulk_collection:
        entities = collection.entities_with_relationships(attributes=["database"])


Create entities by bulk
~~~~~~~~~~~~~~~~~~~~~~~

To create entities:: 

    bulk = {"entities" : [ {
		    "attributes": {"qualifiedName": "my_awesome_data", "name": "my_awesome_data_name", "path": "/my-awesome-path"},
		    "status" : "ACTIVE",
		    "version" : 3,
		    "classifications" : [ {"typeName" : "Customer"}, {"typeName" : "Confidential"}],
		    "typeName" : "hdfs_path"}],
             "referredEntities": {}
            }
    client.entity_bulk.create(data=bulk)

This will create an hdfs_path entity with 2 classifications.
Note that you can pass a list of entities (not limited to 1). 


Delete multiple entities
~~~~~~~~~~~~~~~~~~~~~~~~

To delete a list of entities::

    client.entity_bulk.delete(guid=[GUID1, GUID2])


Associate a tag to multiple entities
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To associate a tag to multiple entities::

    entity_bulk_tag = {"classification": {"typeName": "Confidential"},
	               "entityGuids": [GUID1, GUID2]}
    client.entity_bulk_classification.create(data=entity_bulk_tag) 

This will create the tag 'Confidential' both GUIDs.


Get entity by unique attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To fetch an entity given its type and unique attribute::

    entity = client.entity_unique_attribute('hdfs_path', qualifiedName='/my/awesome/path')


Update entity for subset of attributes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 To update a subset of attributes on an entity which is identified by its type and unique attribute::

    ####  TO BE IMPLEMENTED ####


To delete an entity by unique attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To delete an entity identified by its type and unique attributes::

    entity = client.entity_unique_attribute('hdfs_path', qualifiedName='/my/awesome/path')
    entity.delete()


LineageREST
-----------

Get lineage by GUID
~~~~~~~~~~~~~~~~~~~

To get lineage info about entity identified by GUID::

    lineage = client.lineage_guid(GUID)
    print(lineage.relations)
    print(lineage.lineageDirection)


RelationshipREST
----------------

TO BE DONE...

TypesREST
---------

Get typeDefs
~~~~~~~~~~~~

Typedefs can be seen as a collection of type definitions in Atlas and can accessed with::

    client.typedefs

This only creates an object is not actually requesting the Atlas server. 
Suppose we want to access all elements of type 'enumDefs':: 

    for t in client.typedefs:
        for e in t.enumDefs:
            for el in e.elementDefs:
                print(el.value)

We can access the classification types in a similar way::

    for t in client.typedefs:
        for classification_type in t.classificationDefs:
            print(classification_type.description)

Idem for entityDefs and structDefs. 


Delete typeDefs
~~~~~~~~~~~~~~~

To delete typedefs::

    client.typedefs.delete(data=typedef_dict)

Where `typedef_dict` is the body to pass. 
Here is an example as illustration::

   typedef_dict = {
   "enumDefs":[],
   "structDefs":[],
   "classificationDefs":[],
   "entityDefs":[
      {
         "superTypes":[
           "DataSet"
         ],
         "name":"test_entity_7",
         "description":"test_entity_7",
         "createdBy": "admin",
         "updatedBy": "admin",
         "attributeDefs":[
            {
               "name":"test_7_1",
               "isOptional": True,
               "isUnique": False,
               "isIndexable": False,
               "typeName":"string",
               "valuesMaxCount":1,
               "cardinality":"SINGLE",
               "valuesMinCount":0
            },
           {
               "name":"test_7_2",
               "isOptional": True,
               "isUnique": False,
               "isIndexable": False,
               "typeName":"string",
               "valuesMaxCount":1,
               "cardinality":"SINGLE",
               "valuesMinCount":0
            }
         ]
         
      }
   ]
   } 

Create typeDefs
~~~~~~~~~~~~~~~

To create typedefs::

    client.typedefs.create(data=typedef_dict)

An example for `typedef_dict` is given at the subsection above. 

Update typeDefs
~~~~~~~~~~~~~~~

To update typedefs::

    client.typedefs.update(data=typedef_dict)

An example for `typedef_dict` is given at the subsection above. 


Get typeDefs headers
~~~~~~~~~~~~~~~~~~~~

To get typedefs headers::

    for header in client.typedefs_headers:
        print(header.name)
        print(header.category)


Get classificationDefs by GUID 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get classificationdefs by GUID::

    class_defs = client.classificationdef_guid(CLASSIFICATION_GUID)
    class_defs.name
    class_defs._data


Get classificationDefs by name 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get classificationdefs by name::
    
    CLASSIFICATION_NAME = 'Confidential'
    class_defs = client.classificationdef_name(CLASSIFICATION_NAME)
    class_defs.description


Get entityDefs by GUID 
~~~~~~~~~~~~~~~~~~~~~~

To get entitydefs by GUID::
    
    entity_defs = client.entitydef_guid(ENTITY_GUID)
    entity_defs.description
    

Get entityDefs by name 
~~~~~~~~~~~~~~~~~~~~~~

To get entitydefs by name::

    ENTITY_NAME = 'hdfs_path'
    entity_defs = client.entitydef_name(ENTITY_NAME)
    entity_defs.description


Get enumDefs by GUID 
~~~~~~~~~~~~~~~~~~~~


To get enumdefs by GUID::

    enum_defs = client.enumdef_guid(ENUM_GUID)
    enum_defs.elementDefs


Get enumDefs by name 
~~~~~~~~~~~~~~~~~~~~

To get enumdefs by name::

    ENUM_NAME = 'file_action'
    enum_defs = client.enumdef_name(ENUM_NAME)
    enum_defs.elementDefs


Get relationshipDefs by GUID 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get relationshipdefs by GUID::

    relationship_defs = client.relationshipdef_guid(RELATIONSHIP_GUID)
    relationship_defs._data


Get relationshipDefs by name 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To get relationshipdefs by name::

    relationship_defs = client.relationshipdef_guid(RELATIONSHIP_NAME)
    relationship_defs._data


Get structDefs by GUID 
~~~~~~~~~~~~~~~~~~~~~~

To get structdefs by GUID::

    struct_defs = client.structdef_guid(STRUCT_GUID)
    struct_defs._data

Get structDefs by name 
~~~~~~~~~~~~~~~~~~~~~~

To get structdefs by name::

    struct_defs = client.structdef_guid(STRUCT_NAME)
    struct_defs._data


Get typeDefs by GUID 
~~~~~~~~~~~~~~~~~~~~

To get typedefs by GUID::

    type_defs = client.typedef_guid(TYPE_GUID)
    type_defs._data


Get typeDefs by name 
~~~~~~~~~~~~~~~~~~~~

To get typedefs by name::

    type_defs = client.typedef_guid(TYPE_NAME)
    type_defs._data

AdminREST
---------

Get Admin Metrics
~~~~~~~~~~~~~~~~~

This endpoint is not yet mentioned in the official atlas documentation, but gives the complete
statistics available for Atlas >2.x only. Endpoint is `api/atlas/admin/metrics`::


    for metrics in client.admin_metrics:
        # This gives the entities count for both active and deleted entities
        entity_stats = metrics.entity

        # Provides the general Atlas statistics, about the counts, and different timestamps
        general_stats = metrics.general

        # Provides a list of tags, along with the count of entities using that tag
        tag_stats = metrics.tag
