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

from atlasclient import base, exceptions, events
from atlasclient.utils import normalize_underscore_case, NullHandler

LOG = logging.getLogger(__name__)
LOG.addHandler(NullHandler())


#class EntityCollection(base.DependentModelCollection):
#    def __call__(self, *args, **kwargs):
#        fields = ('guid', 'status', 'createdBy', 'updatedBy', 'createTime', 'updateTime', 'version',)
#        for f in fields:
#            setattr(self, f, self.parent._data['entity'][f])   
#        return super(EntityCollection, self).__call__(*args, **kwargs)
#
#
#class Entity(base.DependentModel):
#     collection_class = EntityCollection
#
#
#class ReferredEntityCollection(base.DependentModelCollection):
#    def __call__(self, *args, **kwargs):
#        #fields = ('guid',)
#        for k, v in self.parent._data['referredEntities'].items():
#            setattr(self, k, v)
#        return super(ReferredEntityCollection, self).__call__(*args, **kwargs)
#
#
#class ReferredEntity(base.DependentModel):
#     collection_class = ReferredEntityCollection

class Entity(base.QueryableModel):
    path = 'entity'
    data_key = 'entity'
    primary_key = 'qualifiedName'


class Classification(base.QueryableModel):
    path = 'classifications'
    data_key = 'classifications'
    primary_key = 'typeName'
    fields = ('typeName', 'attributes')
    
#    def __init__(self, *args, **kwargs): 
#        super(base.QueryableModel, self).__init__(*args, **kwargs)
#        self._href = self._href.replace('classifications/', 'classification/')
 
#    def _generate_input_dict(self, **kwargs):
#        return self._data 
    
    def _generate_input_dict(self, **kwargs):
        if self.data_key:
            data = { self.data_key: {}}
            for field in kwargs:
                if field in self.fields:
                    data[self.data_key][field] = kwargs[field]
                else:
                    data[field] = kwargs[field]
            #import pdb; pdb.set_trace()
            for field in self.fields:
                if hasattr(self, field) and field not in data[self.data_key].keys():
                    data[self.data_key][field] = getattr(self, field)
            return data
        else:
            return kwargs

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
        # /v2/entity/guid/{guid}/classifications
        #import pdb; pdb.set_trace()
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
        data = self._generate_input_dict(**kwargs)
        self.load(self.client.put(self.url, data=data))
        return self


class EntityGuidClassification(Classification):
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
    relationships = {'constraints' : Constraint} 


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

class LineageGuid(base.QueryableModel):
    path = 'lineage/guid'
    data_key = 'lineage_guid'
    primary_key = 'guid'
    fields = ('baseEntityGuid', 'guidEntityMap', 'property1', 'property2', 'relations', 'lineageDirection', 'lineageDepth')
    relationships = {'relations': LineageGuidRelation}

#class Attribute(base.DependentModel):
#    data_key = 'attributes'
#    fields = ('name')
#
#
#class AttributeCollection(base.DependentModelCollection):
#    pass

class FullTextResultCollection(base.DependentModelCollection):
    pass

class FullTextResult(base.DependentModel):
    collection_class = FullTextResultCollection
    data_key = 'fulltext_results'
    fields = ('entity', 'score')

class SearchAttributeCollection(base.QueryableModelCollection):
    def __init__(self, *args, **kwargs):
        self.attrName = kwargs.get('attrName')
        self.attrValuePrefix = kwargs.get('attrValuePrefix')
        self.limit = kwargs.get('limit')
        self.offset = kwargs.get('offset')
        self.typeName = kwargs.get('typeName')
        import pdb; pdb.set_trace()
        super().__init__(self, *args, **kwargs)

    def load(self, response):
        parameters = [attr for attr in ['attrName', 'attrValuePrefix', 'limit', 'offset', 'typeName'] if getattr(self, attr) is not None]
        url = self.url + '?' + '&'.join(parameters)
        model = self.model_class(self, href=self.url)
        model.load(response)
        self._models.append(model)


class SearchAttribute(base.QueryableModel):
    #collection_class = SearchAttributeCollection
    path = 'search/attribute'
    data_key = 'search_attribute'
    
    fields = ('queryType', 'searchParameters', 'queryText', 'type', 'classification', 
              'entities' , 'attributes', 'fullTextResult', 'referredEntities')
    relationships = {'entities': Entity,
                     'attributes': AttributeDef,
                     'fullTextResults': FullTextResult}
