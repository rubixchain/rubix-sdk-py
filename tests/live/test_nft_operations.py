import pytest

from rubix.querier import Querier

from .conftest import requires_funded_account

pytestmark = [pytest.mark.live, requires_funded_account]


# Based on examples/nft_operations.py. The tests depend on each other and run in order,
# sharing what they create through `state`.
@pytest.fixture(scope="module")
def state() -> dict:
    return {}


@pytest.fixture(scope="module")
def querier(client) -> Querier:
    return Querier(client)


def require(state: dict, key: str):
    if key not in state:
        pytest.skip(f"an earlier NFT test did not produce `{key}`")
    return state[key]


def test_deploys_an_nft(funded_signer, querier, nft_files, state):
    artifact_file, metadata_file = nft_files

    response = funded_signer.deploy_nft(
        artifact_file=artifact_file,
        metadata_file=metadata_file,
        nft_value=0.001,
        nft_data="init data",
    )

    assert response.get("error") is None, f"NFT Deployment Failed!: {response.get('error')}"
    nft_address = response["nft_address"]
    assert nft_address.startswith("Qm")
    state["nft_address"] = nft_address

    owned = querier.get_nfts_by_owner(funded_signer.did)
    assert {"nft_id": nft_address, "value": 0.001} in owned


def test_executes_the_nft(funded_signer, querier, state):
    nft_address = require(state, "nft_address")

    response = funded_signer.execute_nft(
        nft_address=nft_address,
        nft_data="test execution data",
        nft_value=0.001,
    )

    assert response["status"] is True, f"NFT Execution Failed!: {response.get('message', '')}"

    states = querier.get_nft_states(nft_address, only_latest_state=False)
    assert len(states) > 1
    assert "test execution data" in [s["data"] for s in states]
    assert states[-1]["data"] == "test execution data"


def test_returns_only_the_latest_nft_state(querier, state):
    nft_address = require(state, "nft_address")

    states = querier.get_nft_states(nft_address, only_latest_state=False)
    latest = querier.get_nft_states(nft_address, only_latest_state=True)
    assert latest == [states[-1]]
    assert latest[0]["data"] == "test execution data"


def test_creates_a_child_nft(funded_signer, querier, state):
    nft_address = require(state, "nft_address")

    response = funded_signer.create_child_nft(
        parent_nft_address=nft_address,
        nft_data="child data",
        nft_value=0.001,
        comment="Test child NFT",
    )

    assert response.get("error") is None, f"Child NFT Creation Failed!: {response.get('error')}"
    assert isinstance(response["tx_id"], str)
    assert len(response["child_nfts"]) > 0
    assert response["child_nfts"][0]["parentNFTId"] == nft_address
    child_nft_address = response["child_nfts"][0]["childNFTId"]

    children = querier.get_child_nfts(nft_address)
    assert child_nft_address in [child["nft_id"] for child in children]
    assert querier.get_parent_nft(child_nft_address)["nft_id"] == nft_address


def test_transfers_the_nft_to_another_did(funded_signer, receiver_did, state):
    nft_address = require(state, "nft_address")

    response = funded_signer.transfer_nft(
        nft_address=nft_address,
        receiver_did=receiver_did,
        nft_value=0.001,
        comment="Test NFT Transfer",
    )

    assert response["status"] is True, f"NFT Transfer Failed!: {response.get('message', '')}"
    assert isinstance(response["result"]["transactionID"], str)
    state["transferred"] = True


# Known issue: transfer_nft does not set `transferNftOwnership`, so the node records the
# transaction but the sender keeps ownership of the NFT. When this starts passing, remove the xfail marker.
@pytest.mark.xfail(strict=True, reason="transfer_nft does not set transferNftOwnership")
def test_moves_nft_ownership_to_the_receiver(receiver_did, querier, state):
    nft_address = require(state, "nft_address")
    require(state, "transferred")

    owned = querier.get_nfts_by_owner(receiver_did) or []
    assert nft_address in [nft["nft_id"] for nft in owned]
