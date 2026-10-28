import pytest

from rubix.querier import Querier

from .conftest import FUNDED_DID, requires_funded_account

pytestmark = pytest.mark.live


@pytest.fixture(scope="module")
def querier(client) -> Querier:
    return Querier(client)


@pytest.fixture(scope="module")
def nfts(querier) -> list:
    return querier.get_all_nft()


def test_lists_all_nfts(nfts):
    assert isinstance(nfts, list)
    assert len(nfts) > 0
    assert isinstance(nfts[0]["TokenID"], str)
    assert isinstance(nfts[0]["TokenValue"], (int, float))
    assert isinstance(nfts[0]["DID"], str)
    assert isinstance(nfts[0]["TransactionID"], str)


@requires_funded_account
@pytest.mark.skipif(FUNDED_DID == "", reason="RUBIX_TEST_DID is not set")
def test_gets_the_rbt_balance_of_a_did(querier):
    balance = querier.get_rbt_balance(FUNDED_DID)
    assert set(balance) == {"balance", "pledged", "locked"}
    assert all(isinstance(value, (int, float)) for value in balance.values())


def test_gets_the_ft_balances_of_a_did(querier):
    balances = querier.get_ft_balances("bafybmicbopex4ydytrtremmculwpo7e5p2uvbkuw2ds775xmkcsc5lglai")
    assert isinstance(balances, list)


def test_gets_the_nfts_owned_by_a_did(querier, nfts):
    owned = querier.get_nfts_by_owner(nfts[0]["DID"])
    assert nfts[0]["TokenID"] in [nft["nft_id"] for nft in owned]


def test_gets_the_nft_token_chain(querier, nfts):
    states = querier.get_nft_states(nfts[0]["TokenID"], only_latest_state=False)
    assert len(states) > 0
    assert set(states[0]) == {"transactionId", "initiator", "epoch", "data"}


def test_gets_the_parent_and_children_of_an_nft(querier, nfts):
    child = next((nft for nft in nfts if nft["ParentTokenID"]), None)
    if child is None:
        pytest.skip("no child NFT found on the node")
    parent_address = child["ParentTokenID"]

    parent = querier.get_parent_nft(child["TokenID"])
    assert parent["nft_id"] == parent_address

    children = querier.get_child_nfts(parent_address)
    assert child["TokenID"] in [nft["nft_id"] for nft in children]

    # An NFT without a parent
    assert querier.get_parent_nft(parent_address) == ""


def test_rejects_invalid_addresses_and_dids_before_calling_the_node(querier):
    with pytest.raises(ValueError, match="Invalid DID: QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG"):
        querier.get_rbt_balance("QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG")

    with pytest.raises(ValueError, match="Invalid NFT address"):
        querier.get_nft_states("bafybmicbopex4ydytrtremmculwpo7e5p2uvbkuw2ds775xmkcsc5lglai")


def test_raises_when_the_node_reports_a_failure(querier):
    with pytest.raises(ValueError, match="Failed to get NFT states: Failed to retrieve nft chain data"):
        querier.get_nft_states("QmYwAPJzv5CZsnA625s3Xf2nemtYgPpHdWEz79ojWnPbdG")
