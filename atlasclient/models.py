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
#    def create(self):
#        """Add classifications to an existing entity represented by a guid."""
#        href = self.url
#        #import pdb; pdb.set_trace()
#        self.load(self.client.post(self, href=href, data=self.parent.entity['classifications']))
#        return self


class EntityGuidClassification(Classification):
    collection_class = EntityGuidClassificationCollection


class EntityGuid(base.QueryableModel):
    path = 'entity/guid'
    data_key = 'entityGuid'
    primary_key = 'guid'
    fields = ('entity', 'referredEntities')
    relationships = {#'entity': Entity,
                     #'referredEntities': ReferredEntity,
                     'classifications': EntityGuidClassification,
                    }

    def _generate_input_dict(self, **kwargs):
        return self._data 
 



