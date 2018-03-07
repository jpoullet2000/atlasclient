try: 
    from mock import MagicMock 
except ImportError: 
    from unittest.mock import MagicMock

from atlasclient.base import Model, QueryableModel
from atlasclient.client import HttpClient

class TestBase():

    def test_model(self, monkeypatch):
        monkeypatch.setattr('atlasclient.base.QueryableModel', MagicMock(QueryableModel))
        monkeypatch.setattr('atlasclient.client.HttpClient', MagicMock(HttpClient))
        queryablemodel = QueryableModel
        httpclient = HttpClient
        queryablemodel.client  = httpclient 
        data = {'entity': {'createdBy': 'owner'}}
        model = Model(parent=queryablemodel, data=data) 
        assert 'parent' in dir(model)
        assert model.identifier is None
