import pytest

from rubix.querier import Querier

from .conftest import requires_funded_account

pytestmark = [pytest.mark.live, requires_funded_account]

# Shared with the rubix-sdk-ts live tests, so the FT is minted only once per account
FT_NAME = "TSSDKFT"


def has_ft(balances, name: str) -> bool:
    return any(balance.get("name") == name for balance in balances or [])


# Based on examples/ft_token_transfer.py
def test_creates_an_ft_once_and_transfers_it(client, funded_signer, receiver_did):
    rubix_querier = Querier(client)

    # Mint the FT only if the funded account has run out of it, to avoid locking RBT on every run
    if not has_ft(rubix_querier.get_ft_balances(funded_signer.did), FT_NAME):
        create_response = funded_signer.create_ft(name=FT_NAME, supply=10, rbt_lock_amount=1)
        assert create_response["status"] is True, f"FT Creation Failed!: {create_response.get('message', '')}"

    response = funded_signer.send_ft(
        receiver_did=receiver_did,
        ft_name=FT_NAME,
        ft_count=1,
        ft_creator_did=funded_signer.did,
        comment="Test FT Transfer",
    )

    assert response["status"] is True, f"FT Transfer Failed!: {response.get('message', '')}"

    assert has_ft(rubix_querier.get_ft_balances(receiver_did), FT_NAME)
