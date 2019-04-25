from pytest_mock import mocker
from pkg_resources import resource_filename
import json
import pytest

from atlasclient import client
from atlasclient import exceptions
GUID = '8bbea92b-d98c-4613-ae6e-1a9d0b4f344b'
RESPONSE_JSON_DIR = 'response_json'
QUERY_JSON_DIR = 'query_json'

@pytest.fixture(scope='class')
def entity_post_response():
    with open('{}/entity_post.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def entity_bulk_response():
    with open('{}/entitybulk_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def entity_bulk_classification_response():
    with open('{}/entitybulkclassification_post.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def entity_guid_response():
    with open('{}/entityguid_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def entity_guid_delete_response():
    with open('{}/entityguid_delete.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='function')
def entity_guid(atlas_client):
    entity_guid = atlas_client.entity_guid(GUID) 
    return(entity_guid)

@pytest.fixture(scope='class')
def entity_guid_classification_response():
    with open('{}/entityguid_classification_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def entity_guid_classifications_post():
    with open('{}/entityguid_classifications_post.json'.format(resource_filename(__name__, QUERY_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def typedefs_response():
    with open('{}/typedefs_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def typedefs_headers_response():
    with open('{}/typedefs_headers_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def relationshipdef_guid_response():
    with open('{}/relationshipdef_guid_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def lineage_guid_response():
    with open('{}/lineage_guid_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def relationship_guid_response():
    with open('{}/relationship_guid_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)

@pytest.fixture(scope='class')
def search_attribute_response():
    with open('{}/search_attribute_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)


class TestEntityREST():
    def test_entity_post(self, mocker, atlas_client, entity_guid_response, entity_post_response):
        mocker.patch.object(atlas_client.client, 'get')
        atlas_client.client.get.return_value = entity_guid_response
        mocker.patch.object(atlas_client.entity_post.client, 'post')
        atlas_client.entity_post.client.post.return_value = entity_post_response
        atlas_client.entity_post.create(data=entity_guid_response)
        atlas_client.entity_post.client.post.assert_called_with(atlas_client.entity_post.url, data=entity_guid_response)


    def test_entity_bulk_get(self, mocker, atlas_client, entity_bulk_response):
        mocker.patch.object(atlas_client.client, 'get')
        atlas_client.entity_bulk.client.get.return_value =  entity_bulk_response 
        params = {'guid': [GUID, '92b3a92b-d98c-4613-ae6e-1a9d0b4f344b']}
        bulk_collection = atlas_client.entity_bulk(**params) 
        for bulk in bulk_collection:
            atlas_client.entity_bulk.client.get.assert_called_with(bulk_collection.url, params=params)
            for entity in bulk.entities:
                assert entity.version == 12345

    def test_entity_bulk_delete(self, mocker, atlas_client, entity_bulk_response):
        mocker.patch.object(atlas_client.client, 'get')
        atlas_client.entity_bulk.client.get.return_value =  entity_bulk_response 
        mocker.patch.object(atlas_client.client, 'delete')
        atlas_client.entity_bulk.client.delete.return_value =  entity_bulk_response 
        params = {'guid': [GUID, '92b3a92b-d98c-4613-ae6e-1a9d0b4f344b']}
        bulk_collection = atlas_client.entity_bulk(**params) 
        for bulk in bulk_collection:
            bulk.delete(**params)
            atlas_client.entity_bulk.client.delete.assert_called_with(bulk_collection.url, params=params)
    
    def test_entity_bulk_create(self, mocker, atlas_client, entity_bulk_response):
        mocker.patch.object(atlas_client.client, 'get')
        atlas_client.entity_bulk.client.get.return_value =  entity_bulk_response 
        mocker.patch.object(atlas_client.client, 'post')
        atlas_client.entity_bulk.client.post.return_value =  entity_bulk_response 
        params = {'guid': [GUID, '92b3a92b-d98c-4613-ae6e-1a9d0b4f344b']}
        bulk_collection = atlas_client.entity_bulk(**params) 
        for bulk in bulk_collection:
            bulk.create()
            atlas_client.entity_bulk.client.post.assert_called_with(bulk_collection.url, data=bulk._data)
    
    def test_entity_bulk_classification_create(self, mocker, atlas_client, entity_bulk_classification_response):
        mocker.patch.object(atlas_client.entity_bulk_classification.client, 'post')
        atlas_client.entity_bulk_classification.client.post.return_value =  entity_bulk_classification_response 
        params = {'guid': [GUID, '92b3a92b-d98c-4613-ae6e-1a9d0b4f344b']}
        atlas_client.entity_bulk_classification.create(data=entity_bulk_classification_response)
        atlas_client.entity_bulk_classification.client.post.assert_called_with(atlas_client.entity_bulk_classification.url, data=entity_bulk_classification_response) 
        
    def test_get_entity_by_guid(self, mocker, entity_guid_response, entity_guid):
        mocker.patch.object(entity_guid.client.client, 'request')
        entity_guid.client.client.request.return_value = entity_guid_response
        assert '/entity/guid/{}'.format(GUID) in entity_guid._href
        #  Loading the data because before that no data were actually loaded (lazy loading) 
        entity_guid.entity
        assert entity_guid._data['entity']['guid'] == GUID
        entity_guid.entity['status'] = 'ACTIVE'
        assert entity_guid._data['entity']['status'] == 'ACTIVE'
        
    def test_update_entity_by_guid(self, mocker, entity_guid_response, entity_guid):    
        mocker.patch.object(entity_guid.client, 'request')
        entity_guid.client.request.return_value = entity_guid_response
        mocker.patch.object(entity_guid.client, 'put')
        attribute = 'description'
        entity_guid.update(attribute=attribute)
        entity_guid.client.put.assert_called_with(entity_guid._href + '?name={}'.format(attribute),
                                                  data=entity_guid.entity['attributes'][attribute])
    
    def test_create_entity_by_guid(self, mocker, entity_guid_response, entity_guid):    
        mocker.patch.object(entity_guid.client, 'post')
        entity_guid.create()
        entity_guid.client.post.assert_called_with(entity_guid._href, data=entity_guid._data)
        
    def test_delete_entity_by_guid(self, mocker, entity_guid_delete_response, entity_guid):
        mocker.patch.object(entity_guid.client.client, 'request')
        entity_guid.client.client.request.return_value = entity_guid_response
        mocker.patch.object(entity_guid.client, 'delete')
        entity_guid.client.delete.return_value = entity_guid_delete_response
        entity_guid.delete()
        entity_guid.client.delete.assert_called_with(entity_guid._href)
        
    def test_get_entity_by_guid_classifications(self, mocker, entity_guid_classification_response, entity_guid): 
        mocker.patch.object(entity_guid.classifications.client, 'get')
        entity_guid.classifications.client.get.return_value = entity_guid_classification_response
        for c in entity_guid.classifications:
            assert 'entity/guid/{guid}/classifications'.format(guid=GUID)
    
    def test_create_entity_by_guid_classifications(self, mocker, entity_guid_classifications_post, entity_guid):
        mocker.patch.object(entity_guid.classifications.client, 'post')
        entity_guid.classifications.client.post.return_value = {}
        entity_guid.classifications.create(data=entity_guid_classifications_post)
        entity_guid.classifications.client.post.assert_called_with(entity_guid.classifications.url, data=entity_guid_classifications_post)
    
    def test_update_entity_by_guid_classifications(self, mocker, entity_guid_classification_response, entity_guid_classifications_post, entity_guid): 
        mocker.patch.object(entity_guid.classifications.client, 'get')
        entity_guid.classifications.client.get.return_value = entity_guid_classification_response
        mocker.patch.object(entity_guid.classifications.client, 'put')
        entity_guid.classifications.client.put.return_value = {}
        entity_guid.classifications.update()
        entity_guid.classifications.client.put.assert_called_with(entity_guid.classifications.url, 
                                                                  data=[{'typeName': 'Confidential'}, {'typeName': None}])
        
         
class TestTypeDefs():
    def test_typedefs_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response
        #  structDefs
        attribute_defs_names = []
        constraint_counter = 0
        for t in atlas_client.typedefs:
            for type_struct in t.structDefs:
                assert hasattr(type_struct, 'name')
                for attribute_def in type_struct.attributeDefs:
                    attribute_defs_names.append(attribute_def.name)
                    for constraint in attribute_def.constraints:
                        constraint_counter += 1
        assert attribute_defs_names == ['attributeName{}'.format(i) for i in range(1,5)]
        assert constraint_counter == 8
        #  enumDefs
        element_defs_values = []
        for t in atlas_client.typedefs:
            for type_class in t.enumDefs:
                assert hasattr(type_class, 'name')
                for element_def in type_class.elementDefs:
                    element_defs_values.append(element_def.value)
        assert element_defs_values == ['...', '...', '...', '...']
        #  classificationDefs
        class_attr_defs_values = []
        supertype_counter = 0
        for t in atlas_client.typedefs:
            for type_class in t.classificationDefs:
                assert hasattr(type_class, 'name')
                for attribute_def in type_class.attributeDefs:
                    class_attr_defs_values.append(attribute_def.name)
                for supertype in type_class.superTypes:
                    supertype_counter += 1

        assert class_attr_defs_values == ['...', '...', '...', '...']
        assert supertype_counter == 4 
        #  entityDefs
        entity_attr_defs_values = []
        supertype_counter = 0
        for t in atlas_client.typedefs:
            for type_entity in t.entityDefs:
                assert hasattr(type_entity, 'name')
                for attribute_def in type_entity.attributeDefs:
                    entity_attr_defs_values.append(attribute_def.name)
                for supertype in type_entity.superTypes:
                    supertype_counter += 1

        assert entity_attr_defs_values == ['...', '...', '...', '...']
        assert supertype_counter == 4 

    def test_typedefs_put(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'get')
        atlas_client.client.get.return_value = typedefs_response
        for t in atlas_client.typedefs:
                mocker.patch.object(t.client, 'put')
                t.client.put.return_value = typedefs_response 
                t.update()
                t.client.put.assert_called_with(t._href, data=t._data)

    def test_typedefs_post(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'get')
        atlas_client.client.get.return_value = typedefs_response
        for t in atlas_client.typedefs:
                mocker.patch.object(t.client, 'post')
                t.client.post.return_value = typedefs_response 
                t.create()
                t.client.post.assert_called_with(t._href, data=t._data)
    
    def test_typedefs_delete(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'get')
        atlas_client.client.get.return_value = typedefs_response
        for t in atlas_client.typedefs:
                mocker.patch.object(t.client, 'delete')
                t.client.delete.return_value = {} 
                t.delete()
                t.client.delete.assert_called_with(t._href, data=typedefs_response)

    def test_typedefs_headers_get(self, mocker, atlas_client, typedefs_headers_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_headers_response
        for h in atlas_client.typedefs_headers:
            assert h.category == 'RELATIONSHIP'
           
    def test_classificationdef_guid_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['classificationDefs'][0]
        c_def = atlas_client.classificationdef_guid(GUID)
        assert c_def.category == 'CLASSIFICATION'
   
    def test_classificationdef_name_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['classificationDefs'][0]
        c_def = atlas_client.classificationdef_name('name')
        assert c_def.category == 'CLASSIFICATION'

    def test_entitydef_guid_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['entityDefs'][0]
        c_def = atlas_client.entitydef_guid(GUID)
        assert c_def.category == 'ENTITY'
   
    def test_entitydef_name_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['entityDefs'][0]
        c_def = atlas_client.entitydef_name('name')
        assert c_def.category == 'ENTITY'

    def test_enumdef_guid_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['enumDefs'][0]
        c_def = atlas_client.enumdef_guid(GUID)
        assert c_def.category == 'ENUM'
   
    def test_enumdef_name_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['enumDefs'][0]
        c_def = atlas_client.enumdef_name('name')
        assert c_def.category == 'ENUM'
    
    def test_relationshipdef_guid_get(self, mocker, atlas_client, relationshipdef_guid_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = relationshipdef_guid_response
        c_def = atlas_client.relationshipdef_guid(GUID)
        assert c_def.relationshipCategory == 'ASSOCIATION'
   
    def test_relationshipdef_name_get(self, mocker, atlas_client, relationshipdef_guid_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = relationshipdef_guid_response
        c_def = atlas_client.relationshipdef_name('name')
        assert c_def.relationshipCategory == 'ASSOCIATION'
    
    def test_structdef_guid_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['structDefs'][0]
        c_def = atlas_client.structdef_guid(GUID)
        assert c_def.category == 'STRUCT'
   
    def test_structdef_name_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['structDefs'][0]
        c_def = atlas_client.structdef_name('name')
        assert c_def.category == 'STRUCT'

    def test_typedef_guid_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['structDefs'][0]
        c_def = atlas_client.typedef_guid(GUID)
        assert c_def.category == 'STRUCT'
   
    def test_typedef_name_get(self, mocker, atlas_client, typedefs_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value = typedefs_response['structDefs'][0]
        c_def = atlas_client.typedef_name('name')
        assert c_def.category == 'STRUCT'

class TestLineageGuid():
    def test_lineage_guid_get(self, mocker, atlas_client, lineage_guid_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value =  lineage_guid_response 
        lineage = atlas_client.lineage_guid(GUID)
        assert lineage.lineageDirection == 'BOTH'

class TestRelationshipREST():
    def test_relationship_guid_get(self, mocker, atlas_client, relationship_guid_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value =  relationship_guid_response 
        relationship = atlas_client.relationship_guid(GUID)
        assert relationship.status == 'ACTIVE'

    def test_relationship_guid_delete(self, mocker, atlas_client, relationship_guid_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value =  relationship_guid_response 
        relationship = atlas_client.relationship_guid(GUID)
        relationship.delete()
 
    def test_relationship_guid_update(self, mocker, atlas_client, relationship_guid_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value =  relationship_guid_response 
        relationship = atlas_client.relationship_guid(GUID)
        relationship.update()
    
    def test_relationship_guid_create(self, mocker, atlas_client, relationship_guid_response):
        mocker.patch.object(atlas_client.client, 'request')
        atlas_client.client.request.return_value =  relationship_guid_response 
        relationship = atlas_client.relationship_guid(GUID)
        with pytest.raises(exceptions.MethodNotImplemented) as e:
            relationship.create()

#    def test_relationship_get(self, mocker, atlas_client, relationship_guid_response):
#        with pytest.raises(exceptions.MethodNotImplemented) as e: 
#            atlas_client.relationship.refresh() 

    def test_relationship_put(self, mocker, atlas_client, relationship_guid_response):
        relationship_collection = atlas_client.relationship(data=relationship_guid_response) 
        for r in relationship_collection:
            assert r._data == relationship_guid_response
            mocker.patch.object(r.client, 'put')
            r.client.put.return_value = relationship_guid_response 
            r.update()
            r.client.put.assert_called_with(r._href, data=r._data)
             
    def test_relationship_post(self, mocker, atlas_client, relationship_guid_response):
        relationship_collection = atlas_client.relationship(data=relationship_guid_response) 
        for r in relationship_collection:
            assert r._data == relationship_guid_response
            mocker.patch.object(r.client, 'post')
            r.client.post.return_value = relationship_guid_response 
            r.create()
            r.client.post.assert_called_with(r._href, data=r._data)
        

class TestDiscoveryREST():
    def test_search_attribute_get(self, mocker, atlas_client, search_attribute_response):
        mocker.patch.object(atlas_client.search_attribute.client, 'get')
        atlas_client.search_attribute.client.get.return_value =  search_attribute_response 
        params = {'attrName': 'attrName', 'attrValue': 'attrVal', 'offset': '1'}
        search_results = atlas_client.search_attribute(**params) 
        for s in search_results:
            assert s.queryType == 'GREMLIN'
            atlas_client.search_attribute.client.get.assert_called_with(s.url, params=params)
        for s in search_results:
            for e in s.entities:
                assert e.attributes['property1'] == {}

    def test_search_basic_get(self, mocker, atlas_client, search_attribute_response):
        mocker.patch.object(atlas_client.search_basic.client, 'get')
        search_attribute_response['queryType'] = 'BASIC'
        atlas_client.search_basic.client.get.return_value = search_attribute_response
        params = {'classification': 'class', 'excludedDeletedEntities': 'True', 'limit': '1'}
        search_results = atlas_client.search_basic(**params) 
        for s in search_results:
            assert s.queryType == 'BASIC'
            atlas_client.search_basic.client.get.assert_called_with(s.url, params=params)
            for e in s.entities:
                assert e.attributes['property1'] == {}

    def test_search_basic_post(self, mocker, atlas_client, search_attribute_response):
        mocker.patch.object(atlas_client.search_basic.client, 'get')
        search_attribute_response['queryType'] = 'BASIC'
        atlas_client.search_basic.client.get.return_value =  search_attribute_response 
        mocker.patch.object(atlas_client.search_basic.client, 'post')
        atlas_client.search_basic.client.post.return_value =  search_attribute_response
        search_results = atlas_client.search_basic
        for s in search_results:
            assert s.queryType == 'BASIC'
            s.create(data=s._data)
            atlas_client.search_basic.client.post.assert_called_with(s.url, data=s._data)

    def test_search_dsl_get(self, mocker, atlas_client, search_attribute_response):
        mocker.patch.object(atlas_client.search_dsl.client, 'get')
        search_attribute_response['queryType'] = 'DSL'
        atlas_client.search_dsl.client.get.return_value =  search_attribute_response 
        params = {'classification': 'class', 'limit': '1'}
        search_results = atlas_client.search_dsl(**params) 
        for s in search_results:
            assert s.queryType == 'DSL'
            atlas_client.search_dsl.client.get.assert_called_with(s.url, params=params)
            for e in s.entities:
                assert e.attributes['property1'] == {}

    def test_search_fulltext_get(self, mocker, atlas_client, search_attribute_response):
        mocker.patch.object(atlas_client.search_fulltext.client, 'get')
        search_attribute_response['queryType'] = 'ATTRIBUTE'
        atlas_client.search_fulltext.client.get.return_value =  search_attribute_response 
        params = {'classification': 'class', 'excludedDeletedEntities': 'True', 'limit': '1'}
        search_results = atlas_client.search_fulltext(**params) 
        for s in search_results:
            assert s.queryType == 'ATTRIBUTE'
            atlas_client.search_fulltext.client.get.assert_called_with(s.url, params=params)
            for e in s.entities:
                assert e.attributes['property1'] == {}
