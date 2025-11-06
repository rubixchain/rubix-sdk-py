import pytest
from rubix.client import RubixClient


def test_client_creation_with_valid_url():
    valid_node_url = "http://128.0.0.1:2345"

    client = RubixClient(valid_node_url)
    
    assert client is not None
