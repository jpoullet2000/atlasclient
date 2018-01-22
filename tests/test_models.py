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
    entity_guid = atlas_client.entityguid(GUID) 
    return(entity_guid)


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
    
