from atlasclient.client import Atlas


class TestClient():

    def test_atlas_client(self):
        client = Atlas('localhost', port=21000, username='admin', password='admin')
        assert client.base_url  == 'http://localhost:21000'
        assert 'headers' in client.client.request_params.keys()
        assert 'X-Requested-By' in client.client.request_params['headers']
        assert 'entity_post' in dir(client) 

    def test_http_client(self):
        pass
