from unittest.mock import MagicMock

import pytest

from rubix.querier import Querier

NFT = "QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"

# Token chains are returned by the node ordered oldest first
CHAIN = [
    {"transactionId": "tx-1", "initiator": "did", "epoch": 1, "data": "init"},
    {"transactionId": "tx-2", "initiator": "did", "epoch": 2, "data": ""},
    {"transactionId": "tx-3", "initiator": "did", "epoch": 3, "data": "latest"},
]


def querier_returning(result) -> Querier:
    client = MagicMock()
    client._make_get_request.return_value = {"status": True, "message": "", "result": result}
    return Querier(client)


@pytest.mark.parametrize("method", ["get_nft_states", "get_smart_contract_states"])
def test_returns_every_state_by_default_or_only_the_latest_one(method):
    querier = querier_returning(CHAIN)

    assert getattr(querier, method)(NFT) == CHAIN
    assert getattr(querier, method)(NFT, only_latest_state=False) == CHAIN
    assert getattr(querier, method)(NFT, only_latest_state=True) == [CHAIN[-1]]


def test_returns_an_empty_chain_as_is_when_only_the_latest_state_is_requested():
    assert querier_returning([]).get_nft_states(NFT, only_latest_state=True) == []
