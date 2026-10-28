import pytest

from rubix.did import get_public_key_for_did

from .conftest import FUNDED_DID, NODE_URL, requires_funded_account

pytestmark = pytest.mark.live


@requires_funded_account
def test_funded_account_did_is_registered_for_its_mnemonic(funded_signer):
    if FUNDED_DID != "":
        assert funded_signer.did == FUNDED_DID

    public_key = get_public_key_for_did(funded_signer.did, NODE_URL)
    assert public_key.hex() == funded_signer.get_keypair().public_key
