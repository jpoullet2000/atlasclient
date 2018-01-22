from atlasclient.client import Atlas


class TestClient():

    def test_atlas_client(self):
        client = Atlas('localhost', port=21000, username='admin', password='admin')
        assert client.base_url  == 'http://localhost:21000'
        assert 'auth' in client.client.request_params.keys()
        assert client.client.request_params['headers'] == {'X-Requested-By': 'python-atlasclient'}

    def test_http_client(self):
        pass
