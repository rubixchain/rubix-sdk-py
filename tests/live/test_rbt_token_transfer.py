import pytest

from rubix.querier import Querier

from .conftest import requires_funded_account

pytestmark = [pytest.mark.live, requires_funded_account]


# Based on examples/rbt_token_transfer.py
def test_transfers_rbt_tokens_and_updates_the_receiver_balance(client, funded_signer, receiver_did):
    rubix_querier = Querier(client)

    before = rubix_querier.get_rbt_balance(receiver_did)

    response = funded_signer.send_rbt_tokens(
        receiver_did=receiver_did,
        rbt_amount=0.001,
        memo="Test RBT Transfer",
    )

    assert response["status"] is True, f"RBT Transfer Failed!: {response.get('message', '')}"
    assert isinstance(response["result"]["transactionID"], str)

    after = rubix_querier.get_rbt_balance(receiver_did)
    assert after["balance"] == pytest.approx(before["balance"] + 0.001, abs=1e-6)
