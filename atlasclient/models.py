#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Defines all the model classes for the various parts of the API.
"""

import logging
import json
import os
import time
import six

from atlasclient import base, exceptions, events
from atlasclient.utils import normalize_underscore_case, NullHandler

LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


class EntityCollection(base.DependentModelCollection):
    def __init__(self, client, model_class, parent=None):
        self.client = client
        self.model_class = model_class
        self.parent = parent
        self._is_inflated = True
        self._models = []
        for entity in self.parent._data['entities']:
            model = self.model_class(self, data=entity)
            self._models.append(model)
        self._iter_marker = 0
    
    def __call__(self, *args):
        self._is_inflated = True
        self._models = []
        for entity in self.parent._data['entities']:
            model = self.model_class(self, data=entity)
            self._models.append(model)
        return self


class Entity(base.DependentModel):
    collection_class = EntityCollection
    fields = ('guid', 'status', 'displayText', 'classificationNames', 'typeName', 'attributes', 'createdBy', 'updatedBy', 'createTime', 'updateTime', 'version',)


class EntityPostCollection(base.QueryableModelCollection):
    def __call__(self, *args, **kwargs):
        """
        """
        if 'data' not in kwargs:
            raise exceptions.BadRequest(method=self.__call__, details='This class should be called with the argument "data="')
        self._models = []
        self._is_inflated = True
        model = self.model_class(self,
                                 href=self.url,
                                 data=kwargs.get('data'))
        self._models.append(model)
        return self

    @events.evented
    def create(self, data, **kwargs):
        """
        Update a resource by passing in modifications via keyword arguments.
        """
        self.client.post(self.url, data=data)


class EntityPost(base.QueryableModel):
    """
        EntityPost resource is only used to post data to the Atlas server. The body structure is different from the
        REST response structure. Fields correspond to the body structure.
    """
    collection_class = EntityPostCollection
    path = 'entity'
    data_key = 'entity_post'
    fields = ('entity', 'referredEntities')

    @events.evented
    def delete(self, **kwargs):
        """
        Delete is not allowed for this resource
        """
        raise exceptions.MethodNotImplemented(method=self.delete, details='The method delete is not available for this resource')

    @events.evented
    def update(self, **kwargs):
        """
        Update is not allowed for this resource
        """
        raise exceptions.MethodNotImplemented(method=self.update, details='The method update is not available for this resource')

class ClassificationItemCollection(base.DependentModelCollection):
    def __init__(self, client, model_class, parent=None):
        self.client = client
        self.model_class = model_class
        self.parent = parent
        self._is_inflated = False
        self._models = []
        for classification_item in self.parent._data['list']:
            model = self.model_class(self, data=classification_item)
            self._models.append(model)
        self._iter_marker = 0


class ClassificationItem(base.DependentModel):
    collection_class = ClassificationItemCollection
    fields = ('typeName', )


class Classification(base.QueryableModel):
    path = 'classifications'
    data_key = 'classifications'
    fields = ('sortType', 'list', 'totalCount', 'startIndex', 'pageSize')
    relationships = {'list': ClassificationItem}
    #primary_key = 'typeName'
    #fields = ('typeName', 'attributes')

#    def _generate_input_dict(self, **kwargs):
#        if self.data_key:
#            data = {self.data_key: {}}
#            for field in kwargs:
#                if field in self.fields:
#                    data[self.data_key][field] = kwargs[field]
#                else:
#                    data[field] = kwargs[field]
#            for field in self.fields:
#                if hasattr(self, field) and field not in data[self.data_key].keys():
#                    data[self.data_key][field] = getattr(self, field)
#            return data
#        else:
#            return kwargs

    @events.evented
    def create(self, **kwargs):
        """Create a new instance of this resource type.

        As a general rule, the identifier should have been provided, but in
        some subclasses the identifier is server-side-generated.  Those classes
        have to overload this method to deal with that scenario.
        """
        if self.primary_key in kwargs:
            del kwargs[self.primary_key]
        data = self._generate_input_dict(**kwargs)
        self.load(self.client.post('/'.join(self.url.split('/')[:-1]) + 's', data=data))
        return self

    @events.evented
    def update(self, **kwargs):
        """Update a resource by passing in modifications via keyword arguments.

        """
        data = self._generate_input_dict(**kwargs)
        self.load(self.client.put('/'.join(self.url.split('/')[:-1]) + 's', data=data))
        return self


class EntityGuidClassificationCollection(base.QueryableModelCollection):

    def load(self, response):
        model = self.model_class(self,
                                 href=self.url)
        model.load(response)
        self._models.append(model)

    def _generate_input_dict(self, **kwargs):
        data = {'classifications': []}
        for model in self._models:
            model_data = {}
            for field in model.fields:
                model_data[field] = getattr(model, field)
            data['classifications'].append(model_data)
        return data

    @events.evented
    def update(self, **kwargs):
        """Update a resource by passing in modifications via keyword arguments.

        """
        data = []
        for c in self:
            for classification_item in c.list:
                class_item_dict = dict()
                for field in classification_item.fields:
                        class_item_dict[field] = getattr(classification_item, field)
                data.append(class_item_dict)
        self.load(self.client.put(self.url, data=data))
        return self

    def create(self, data, **kwargs):
        """ 
        Create classifitions for specific entity
        """
        self.client.post(self.url, data=data)


class EntityGuidClassification(base.QueryableModel):
    path = 'classifications'
    #data_key = 'classifications'
    fields = ('sortType', 'list', 'totalCount', 'startIndex', 'pageSize')
    relationships = {'list': ClassificationItem}
    collection_class = EntityGuidClassificationCollection


class EntityGuid(base.QueryableModel):
    path = 'entity/guid'
    data_key = 'entity_guid'
    primary_key = 'guid'
    fields = ('entity', 'referredEntities')
    relationships = {'classifications': EntityGuidClassification,
                     }

    def _generate_input_dict(self, **kwargs):
        return self._data

    
    def update(self, attribute):
        if attribute not in self.entity['attributes']:
                raise exceptions.BadRequest(method=self.update, 
                                            details='The attribute {} does not exist for {}'.format(attribute,
                                                                                                    self.entity['typeName'])) 
        self.load(self.client.put(self.url + '?name={}'.format(attribute),
                                  data=self.entity['attributes'][attribute]))
        return(self._data)


class EntityUniqueAttributeCollection(base.QueryableModelCollection):
    def __call__(self, *args, **kwargs):
        if len(args) == 1:
            identifier = str(args[0])

        if kwargs is None:
                raise exceptions.BadRequest(details='An attribute should be given (e.g. qualifiedName="/my/hdfs/path")')
        
        self._is_inflated = False
        self._filter = {}
        self._models = []
        if kwargs:
            prefix = self.model_class.data_key
            for (key, value) in kwargs.items():
                if self.model_class.use_key_prefix:
                    key = '/'.join([prefix, key])
                if not isinstance(value, six.string_types):
                    value = json.dumps(value)
                self._filter[key] = value
        filter_list = ['{}={}'.format(k, v) for k, v in self._filter.items()]
        return self.model_class(self, href='/'.join([self.url, identifier]) + '?attr:' + '&'.join(filter_list),
                                data={self.model_class.primary_key: identifier})


class EntityUniqueAttribute(base.QueryableModel):
    collection_class = EntityUniqueAttributeCollection
    path = 'entity/uniqueAttribute/type'
    data_key = 'entity_unique_attribute'
    primary_key = 'typeName'
    fields = ('entity', 'referredEntities')
    relationships = {'classifications': EntityGuidClassification,
                     }


class EntityBulkCollection(base.QueryableModelCollection):
    def load(self, response):
        model = self.model_class(self, href=self.url)
        model.load(response)
        self._models.append(model)

    def create(self, data, **kwargs):
        """ 
        Create classifitions for specific entity
        """
        self.client.post(self.url, data=data)
    
    def delete(self, guid):
         """
         Delete guid 
         """
         self.client.delete(self.url, params={'guid': guid})


class EntityBulk(base.QueryableModel):
    collection_class = EntityBulkCollection
    path = 'entity/bulk'
    data_key = 'entity_bulk'
    fields = ('entities', 'referredEntities')
    relationships = {'entities': Entity}

    def inflate(self):
        """Load the resource from the server, if not already loaded."""
        if not self._is_inflated:
            if self._is_inflating:
                # catch infinite recursion when attempting to inflate
                # an object that doesn't have enough data to inflate
                msg = ("There is not enough data to inflate this object.  "
                       "Need either an href: {} or a {}: {}")
                msg = msg.format(self._href, self.primary_key, self._data.get(self.primary_key))
                raise exceptions.ClientError(msg)

            self._is_inflating = True
            self.load(self._data)
            self._is_inflated = True
            self._is_inflating = False
        return self


class EntityBulkClassification(base.QueryableModel):
    path = 'entity/bulk/classification'
    data_key = 'entity_bulk_classification'
    fields = ('classification', 'entityGuids')

    def _generate_input_dict(self, **kwargs):
        return(kwargs)

    def create(self, data, **kwargs):
        """ 
        Create classifitions for specific entity
        """
        self.client.post(self.url, data=data)


class ConstraintCollection(base.DependentModelCollection):
    def __init__(self, client, model_class, parent=None):
        self.client = client
        self.model_class = model_class
        self.parent = parent
        self._is_inflated = False
        self._models = []
        for constraint in self.parent._data['constraints']:
            model = self.model_class(self, data=constraint)
            self._models.append(model)
        self._iter_marker = 0


class Constraint(base.DependentModel):
    collection_class = ConstraintCollection
    data_key = 'constraints'
    fields = ()


class AttributeDefCollection(base.DependentModelCollection):
    def __init__(self, client, model_class, parent=None):
        self.client = client
        self.model_class = model_class
        self.parent = parent
        self._is_inflated = False
        self._models = []
        for attributeDef in self.parent._data['attributeDefs']:
            model = self.model_class(self, data=attributeDef)
            self._models.append(model)
        self._iter_marker = 0


class AttributeDef(base.DependentModel):
    collection_class = AttributeDefCollection
    data_key = 'attributedefs'
    primary_key = 'name'
    fields = ('name', 'typeName', 'isOptional',
              'cardinality', 'valuesMinCount',
              'valuesMaxCount', 'isUnique',
              'isIndexable', 'defaultValue',
              'constraints'
              )
    relationships = {'constraints': Constraint}


class StructDefCollection(base.DependentModelCollection):
    pass


class StructDef(base.DependentModel):
    collection_class = StructDefCollection
    data_key = 'structdefs'
    primary_key = 'name'
    fields = ('name', 'category', 'defaultValue', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime', 'version',
              'description', 'typeVersion', 'options', 'attributeDefs')
    relationships = {'attributeDefs': AttributeDef}


class ElementDefCollection(base.DependentModelCollection):
    def __init__(self, client, model_class, parent=None):
        self.client = client
        self.model_class = model_class
        self.parent = parent
        self._is_inflated = False
        self._models = []
        for elementDef in self.parent._data['elementDefs']:
            model = self.model_class(self, data=elementDef)
            self._models.append(model)
        self._iter_marker = 0


class ElementDef(base.DependentModel):
    collection_class = ElementDefCollection
    data_key = 'elementdefs'
    primary_key = 'ordinal'
    fields = ('ordinal', 'description', 'value',)


class EnumDefCollection(base.DependentModelCollection):
    pass


class EnumDef(base.DependentModel):
    collection_class = EnumDefCollection
    data_key = 'enumdefs'
    primary_key = 'name'
    fields = ('name', 'category', 'defaultValue', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime', 'version',
              'description', 'typeVersion', 'options', 'elementDefs')
    relationships = {'elementDefs': ElementDef}


class ClassificationDefCollection(base.DependentModelCollection):
    pass


class ClassificationDef(base.DependentModel):
    collection_class = ClassificationDefCollection
    data_key = 'classificationdefs'
    primary_key = 'name'
    fields = ('superTypes',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class EntityDefCollection(base.DependentModelCollection):
    pass


class EntityDef(base.DependentModel):
    collection_class = EntityDefCollection
    data_key = 'entitydefs'
    primary_key = 'name'
    fields = ('superTypes',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class TypeDefHeaderCollection(base.QueryableModelCollection):
    pass


class TypeDefHeader(base.QueryableModel):
    collection_class = TypeDefHeaderCollection
    path = 'types/typedefs/headers'
    data_key = 'typedefs_headers'
    primary_key = 'guid'
    fields = ('guid', 'name', 'category')


class TypeDefs(base.QueryableModelCollection):
    def load(self, response):
        model = self.model_class(self, href=self.url)
        model.load(response)
        self._models.append(model)

    @events.evented
    def create(self, data, **kwargs):
        self.client.post(self.url, data=data)
        return self

    @events.evented
    def update(self, data, **kwargs):
        self.client.put(self.url, data=data)
        return self

    @events.evented
    def delete(self, data, **kwargs):
        self.client.delete(self.url, data=data)
        return self

class TypeDef(base.QueryableModel):
    collection_class = TypeDefs
    path = 'types/typedefs'
    data_key = 'typedefs'
    primary_key = ''
    fields = ('empty')
    relationships = {'structDefs': StructDef,
                     'enumDefs': EnumDef,
                     'classificationDefs': ClassificationDef,
                     'entityDefs': EntityDef,
                     }

    def load(self, response):
        self._data.update(response)
        for rel in [x for x in response if x in self.relationships]:
            rel_class = self.relationships[rel]
            collection = rel_class.collection_class(self.client, rel_class, parent=self)
            self._relationship_cache[rel] = collection(response[rel])

    def delete(self):
        self.client.delete(self.url, data=self._data)
        self._data = {}
        return self


class ClassificationDefGuid(base.QueryableModel):
    path = 'types/classificationdef/guid'
    data_key = 'classificationdef_guid'
    primary_key = 'guid'
    fields = ('superTypes',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class ClassificationDefName(base.QueryableModel):
    path = 'types/classificationdef/name'
    data_key = 'classificationdef_name'
    primary_key = 'name'
    fields = ('superTypes',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class EntityDefGuid(base.QueryableModel):
    path = 'types/entitydef/guid'
    data_key = 'entitydef_guid'
    primary_key = 'guid'
    fields = ('superTypes',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class EntityDefName(base.QueryableModel):
    path = 'types/entitydef/name'
    data_key = 'entitydef_name'
    primary_key = 'name'
    fields = ('superTypes',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class EnumDefGuid(base.QueryableModel):
    path = 'types/enumdef/guid'
    data_key = 'enumdef_guid'
    primary_key = 'guid'
    fields = ('name', 'category', 'defaultValue', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime', 'version',
              'description', 'typeVersion', 'options', 'elementDefs')
    relationships = {'elementDefs': ElementDef}


class EnumDefName(base.QueryableModel):
    path = 'types/enumdef/name'
    data_key = 'enumdef_name'
    primary_key = 'name'
    fields = ('name', 'category', 'defaultValue', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime', 'version',
              'description', 'typeVersion', 'options', 'elementDefs')
    relationships = {'elementDefs': ElementDef}

    
class RelationshipDefGuid(base.QueryableModel):
    path = 'types/relationshipdef/guid'
    data_key = 'relationshipdef_guid'
    primary_key = 'guid'
    fields = ('relationshipCategory',
              'propagateTags',
              'endDef1',
              'endDef2',
              'relationshipLabel',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class RelationshipDefName(base.QueryableModel):
    path = 'types/relationshipdef/name'
    data_key = 'relationshipdef_name'
    primary_key = 'name'
    fields = ('relationshipCategory',
              'propagateTags',
              'endDef1',
              'endDef2',
              'relationshipLabel',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class StructDefGuid(base.QueryableModel):
    path = 'types/structdef/guid'
    data_key = 'structdef_guid'
    primary_key = 'guid'
    fields = ('superTypes',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class StructDefName(base.QueryableModel):
    path = 'types/structdef/name'
    data_key = 'structdef_name'
    primary_key = 'name'
    fields = ('superTypes',
              'attributeDefs',
              'category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')
    relationships = {'attributeDefs': AttributeDef,
                     }


class TypeDefGuid(base.QueryableModel):
    path = 'types/typedef/guid'
    data_key = 'typedef_guid'
    primary_key = 'guid'
    fields = ('category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')


class TypeDefName(base.QueryableModel):
    path = 'types/typedef/name'
    data_key = 'typedef_name'
    primary_key = 'name'
    fields = ('category', 'guid', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'name', 'description', 'typeVersion',
              'options')


class LineageGuidRelationCollection(base.DependentModelCollection):
    pass


class LineageGuidRelation(base.DependentModel):
    collection_class = LineageGuidRelationCollection
    data_key = 'lineage_guid_relations'
    fields = ('fromEntityId',
              'toEntityId',
              )


class LineageGuidCollection(base.QueryableModelCollection):
    def __call__(self, *args, **kwargs):
        if len(args) == 1:
            identifier = str(args[0])

        if kwargs is None:
                raise exceptions.BadRequest(details='An attribute should be given (e.g. qualifiedName="/my/hdfs/path")')
        
        self._is_inflated = False
        self._filter = {}
        self._models = []
        url_path_filter = ''
        if kwargs:
            prefix = self.model_class.data_key
            for (key, value) in kwargs.items():
                if self.model_class.use_key_prefix:
                    key = '/'.join([prefix, key])
                if not isinstance(value, six.string_types):
                    value = json.dumps(value)
                self._filter[key] = value
            filter_list = ['{}={}'.format(k, v) for k, v in self._filter.items()]
            url_path_filter = '?' + '&'.join(filter_list)
        return self.model_class(self, href='/'.join([self.url, identifier]) + url_path_filter, 
                                data={self.model_class.primary_key: identifier})
    

class LineageGuid(base.QueryableModel):
    path = 'lineage'
    data_key = 'lineage_guid'
    fields = ('baseEntityGuid', 'guidEntityMap', 'property1', 'property2', 'relations', 'lineageDirection', 'lineageDepth')
    relationships = {'relations': LineageGuidRelation}
    collection_class = LineageGuidCollection
 

class RelationshipGuid(base.QueryableModel):
    path = 'relationship/guid'
    data_key = 'relationship_guid'
    primary_key = 'guid'
    fields = ('guid', 'status', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'end1', 'end2', 'label', 'typeName', 'attributes')

    @events.evented
    def update(self, **kwargs):
        """Update a resource by passing in modifications via keyword arguments.

        """
        data = self._generate_input_dict(**kwargs)
        url = self.parent.url + '/relationship'
        self.load(self.client.put(url, data=data))
        return self

    def create(self, **kwargs):
        """Raise error since guid cannot be duplicated
        """
        raise exceptions.MethodNotImplemented(method=self.create, url=self.url, details='GUID cannot be duplicated, to create a new GUID use the relationship resource')


class RelationshipCollection(base.QueryableModelCollection):
    def __call__(self, *args, **kwargs):
        """

        """
        if 'data' not in kwargs:
            raise exceptions.BadRequest(method=self.__call, details='This class should be called with the argument "data="')
        self._models = []
        self._is_inflated = True
        model = self.model_class(self,
                                 href=self.url,
                                 data=kwargs.get('data'))
        self._models.append(model)
        return self


class Relationship(base.QueryableModel):
    collection_class = RelationshipCollection
    path = 'relationship'
    data_key = 'relationship'
    primary_key = 'guid'
    fields = ('guid', 'status', 'createdBy',
              'updatedBy', 'createTime', 'updateTime',
              'version', 'end1', 'end2', 'label', 'typeName', 'attributes')

    @events.evented
    def update(self, **kwargs):
        """Update a resource by passing in modifications via keyword arguments.

        """
        data = self._generate_input_dict(**kwargs)
        self.client.put(self.url, data=data)
        return self

    @events.evented
    def create(self, **kwargs):
        """Update a resource by passing in modifications via keyword arguments.

        """
        data = self._generate_input_dict(**kwargs)
        self.client.post(self.url, data=data)
        return self


class FullTextResultCollection(base.DependentModelCollection):
    pass


class FullTextResult(base.DependentModel):
    collection_class = FullTextResultCollection
    data_key = 'fulltext_results'
    fields = ('entity', 'score')


class SearchAttributeCollection(base.QueryableModelCollection):
    def load(self, response):
        model = self.model_class(self, href=self.url)
        model.load(response)
        self._models.append(model)


class SearchAttribute(base.QueryableModel):
    collection_class = SearchAttributeCollection
    path = 'search/attribute'
    data_key = 'search_attribute'

    fields = ('queryType', 'searchParameters', 'queryText', 'type', 'classification',
              'entities', 'attributes', 'fullTextResult', 'referredEntities')
    relationships = {'entities': Entity,
                     'attributes': AttributeDef,
                     'fullTextResults': FullTextResult}

    def inflate(self):
        """Load the resource from the server, if not already loaded."""
        if not self._is_inflated:
            if self._is_inflating:
                # catch infinite recursion when attempting to inflate
                # an object that doesn't have enough data to inflate
                msg = ("There is not enough data to inflate this object.  "
                       "Need either an href: {} or a {}: {}")
                msg = msg.format(self._href, self.primary_key, self._data.get(self.primary_key))
                raise exceptions.ClientError(msg)

            self._is_inflating = True
            self.load(self._data)
            self._is_inflated = True
            self._is_inflating = False
        return self

class SearchBasicCollection(base.QueryableModelCollection):
    def load(self, response):
        model = self.model_class(self, href=self.url)
        model.load(response)
        self._models.append(model)


class SearchBasic(base.QueryableModel):
    collection_class = SearchBasicCollection
    path = 'search/basic'
    data_key = 'search_basic'

    fields = ('queryType', 'searchParameters', 'queryText', 'type', 'classification',
              'entities', 'attributes', 'fullTextResult', 'referredEntities')
    relationships = {'entities': Entity,
                     'attributes': AttributeDef,
                     'fullTextResults': FullTextResult}


class SearchDslCollection(base.QueryableModelCollection):
    def load(self, response):
        model = self.model_class(self, href=self.url)
        model.load(response)
        self._models.append(model)


class SearchDsl(base.QueryableModel):
    collection_class = SearchDslCollection
    path = 'search/dsl'
    data_key = 'search_dsl'

    fields = ('queryType', 'searchParameters', 'queryText', 'type', 'classification',
              'entities', 'attributes', 'fullTextResult', 'referredEntities')
    relationships = {'entities': Entity,
                     'attributes': AttributeDef,
                     'fullTextResults': FullTextResult}


class SearchFulltextCollection(base.QueryableModelCollection):
    def load(self, response):
        model = self.model_class(self, href=self.url)
        model.load(response)
        self._models.append(model)


class SearchFulltext(base.QueryableModel):
    collection_class = SearchFulltextCollection
    path = 'search/fulltext'
    data_key = 'search_fulltext'
    fields = ('queryType', 'searchParameters', 'queryText', 'type', 'classification',
              'entities', 'attributes', 'fullTextResult', 'referredEntities')
    relationships = {'entities': Entity,
                     'attributes': AttributeDef,
                     'fullTextResults': FullTextResult}
