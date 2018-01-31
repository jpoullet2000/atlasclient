from pytest_mock import mocker
from atlasclient import client
from pkg_resources import resource_filename
import json
import pytest

GUID = '8bbea92b-d98c-4613-ae6e-1a9d0b4f344b'
RESPONSE_JSON_DIR = 'response_json'


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
def search_attribute_response():
    with open('{}/search_attribute_get.json'.format(resource_filename(__name__, RESPONSE_JSON_DIR))) as json_data:
            response = json.load(json_data)
    return(response)


class TestEntityByGuid():
    def test_get_entity_by_guid(self, mocker, entity_guid_response, entity_guid):
        mocker.patch.object(entity_guid.client.client, 'request')
        entity_guid.client.client.request.return_value = entity_guid_response
        assert '/entity/guid/{}'.format(GUID) in entity_guid._href
        #  Loading the data because before that no data were actually loaded (lazy loading) 
        entity_guid.entity
        assert entity_guid._data['entity']['guid'] == GUID
        entity_guid.entity['status'] = 'ACTIVE'
        assert entity_guid._data['entity']['status'] == 'ACTIVE'
        
        #assert entity_guid.entity().status == 'DELETED' 
        #assert entity_guid.entity().guid == GUID
        #assert 'property1' in entity_guid.referredEntities().__dict__
    
    def test_update_entity_by_guid(self, mocker, entity_guid_response, entity_guid):    
        mocker.patch.object(entity_guid.client, 'put')
        entity_guid.update()
        entity_guid.client.put.assert_called_with(entity_guid._href, data=entity_guid._data)
    
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
        

    def test_create_entity_by_guid_classifications(self, mocker, entity_guid_response, entity_guid): 
        classification_type_name = 'classtype1'
        mocker.patch.object(entity_guid.classifications(classification_type_name).client.client, 'request')
        entity_guid.classifications(classification_type_name).client.client.request.return_value = entity_guid_response['entity']['classifications'][0]
        new_typename = 'classtype2'
        attributes = {'property1': {'name': 'property1_name'}}
        mocker.patch.object(entity_guid.classifications(new_typename).client, 'post')
        # there is no /v2/entity/guid/{guid}/classification/{classificationName} for posting new data
        # posting a new classification involves posting all classifications at once
        entity_guid.classifications.create(new_typename, attributes=attributes)
        url = '/'.join(entity_guid.classifications(new_typename).url.split('/')[:-1]) + 's'
        new_classification = {'classifications': {'typeName': new_typename, 'attributes': attributes}}
        entity_guid.classifications.client.post.assert_called_with(url, data=new_classification)

    def test_get_entity_by_guid_classifications(self, mocker, entity_guid_response, entity_guid): 
        classification_type_name = 'classtype1'
        mocker.patch.object(entity_guid.classifications(classification_type_name).client.client, 'request')
        entity_guid.classifications(classification_type_name).client.client.request.return_value = entity_guid_response['entity']['classifications'][0]
        assert 'entity/guid/{guid}/classification/{classification}'.format(guid=GUID, classification=classification_type_name) in entity_guid.classifications(classification_type_name)._href
        assert entity_guid.classifications('classtype1').typeName == classification_type_name
        mocker.patch.object(entity_guid.classifications.client.client, 'request')
        entity_guid.classifications.client.client.request.return_value = entity_guid_response['entity']['classifications']
        assert classification_type_name == entity_guid.classifications.next()._data['typeName']

    def test_update_entity_by_guid_classifications(self, mocker, entity_guid_response, entity_guid):
        mocker.patch.object(entity_guid.client.client, 'request')
        entity_guid.client.client.request.return_value = entity_guid_response
        entity_guid.entity
        entity_guid.classifications
        mocker.patch.object(entity_guid.classifications.client.client, 'request')
        entity_guid.classifications.client.client.request.return_value = entity_guid_response['entity']['classifications']
        mocker.patch.object(entity_guid.classifications.client, 'put')
        # lazy loading, we need to refresh the data 
        entity_guid.classifications.refresh()
        entity_guid.classifications.update()
        url = entity_guid.classifications.url
        entity_guid.classifications.client.put.assert_called_with(url, data={'classifications': entity_guid.entity['classifications']})

    def test_get_entity_guid_classification(self, mocker, entity_guid_response, entity_guid):
        assert entity_guid.classifications('classtype1').typeName == 'classtype1'

    def test_delete_entity_guid_classification(self, mocker, entity_guid_response, entity_guid):
        mocker.patch.object(entity_guid.classifications('classtype1').client, 'delete')
        entity_guid.classifications('classtype1').client.delete.return_value = {}
        entity_guid.classifications('classtype1').delete()
        entity_guid.client.delete.assert_called_with(entity_guid.classifications('classtype1')._href)

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

class TestSearchAttribute():
    def test_search_attribute_get(self, mocker, atlas_client, search_attribute_response):
        mocker.patch.object(atlas_client.search_attribute.client, 'get')
        atlas_client.search_attribute.client.get.return_value =  search_attribute_response 
        atlas_client.search_attribute(attrName='attrName', attrValue='attrVal', offset=1) 
        #for sr in atlas_client.search_attribute:
        #    assert sr.queryText == '...'
