import os
import shutil
import pytest

from rubix.crypto.account import load_account_from_file, save_account_to_file

def test_save_and_load_keys():
    """Test saving and loading of Secp256k1 keys to and from files."""
    tmppath = os.path.abspath(os.path.join(os.getcwd(), 'tests', 'fixtures'))

    # Sample keys and DID
    public_key = bytes.fromhex("03b8edb32c69e16b8d30de87b48aedc4fa09f1643fbaa3e85dbb1932498ea94b0a")
    private_key = bytes.fromhex("e32a09e939376358c37c8780beb632f5cf2fa12c8a53bc77984e60964fd59c78")
    did = "bafybmicbopex4ydytrtremmculwpo7e5p2uvbkuw2ds775xmkcsc5lglai"
    passphrase = "testpassphrase"

    # Save keys to temporary directory
    save_account_to_file(str(tmppath), public_key, private_key, did, "nero", passphrase=passphrase)

    # Load keys back
    account = load_account_from_file(str(tmppath), "nero", passphrase=passphrase)

    # Verify loaded keys
    assert account.keypair.public_key == public_key.hex()
    assert account.keypair.private_key == private_key.hex()

    with pytest.raises(Exception):
        load_account_from_file(str(tmppath), "nero", passphrase="wrongpassphrase")

    shutil.rmtree(tmppath)

def test_multiple_dir_in_alias_dir():
    tmppath = os.path.abspath(os.path.join(os.getcwd(), 'tests', 'fixtures'))

    # Sample keys and DID
    public_key = bytes.fromhex("03b8edb32c69e16b8d30de87b48aedc4fa09f1643fbaa3e85dbb1932498ea94b0a")
    private_key = bytes.fromhex("e32a09e939376358c37c8780beb632f5cf2fa12c8a53bc77984e60964fd59c78")
    did = "bafybmicbopex4ydytrtremmculwpo7e5p2uvbkuw2ds775xmkcsc5lglai"
    passphrase = "testpassphrase"

    # Save keys to temporary directory
    save_account_to_file(str(tmppath), public_key, private_key, did, "nero", passphrase=passphrase)

    with pytest.raises(Exception):
        save_account_to_file(str(tmppath), public_key, private_key, "bafybmiffsqtxnrinhp4c7sa3y3pju5whxdcf3ndzjxqdbeglgw3yzcnkkm", "nero", passphrase=passphrase)
    
    shutil.rmtree(tmppath)
    