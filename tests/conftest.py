import pytest
from atlasclient.client import Atlas


@pytest.fixture(scope='module')
def atlas_client():
    client = Atlas('localhost', port=21000, username='admin', password='admin')
    return(client)
