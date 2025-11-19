import pytest
from rubix.client import RubixClient


def test_client_creation_with_valid_url():
    valid_node_url = "http://128.0.0.1:2345"

    client = RubixClient(valid_node_url)
    
    assert client is not None

    client_default_url = RubixClient()

    assert client_default_url is not None
    assert client_default_url.node_url == "http://localhost:20000", "Default node URL should be http://localhost:20000"
