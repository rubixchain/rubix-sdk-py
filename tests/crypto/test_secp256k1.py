from rubix.crypto.secp256k1 import Secp256k1Keypair


def test_secp256k1_keypair_from_private_key():
    """Test the generation of a Secp256k1 keypair from a private key."""
    private_key_hex = "1e99423a4edf5c3d2e8f6b8c3f4e5d6c7b8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c"
    private_key_bytes = bytes.fromhex(private_key_hex)

    keypair = Secp256k1Keypair.from_private_key(private_key_bytes)

    assert isinstance(keypair, Secp256k1Keypair)
    assert keypair.public_key is not None
    assert isinstance(keypair.public_key, str)
    assert len(keypair.public_key) == 66, f"expected compressed public key length of 66 hex characters, got {len(keypair.public_key)}"

def test_secp256k1_keypair_from_mnemonic_seed():
    """Test the generation of a Secp256k1 keypair from a mnemonic seed."""
    mnemonic_seed_hex = "1884e5ddc2a5fb783f60803868cffaef1af1ce36e6686357c9c5dd6c80b63d698d78a8db3cab0404ecd3d966a00b9d51e4ac783997f78f64a1b24152e09ec524"
    mnemonic_seed_bytes = bytes.fromhex(mnemonic_seed_hex)

    keypair = Secp256k1Keypair.from_mnemonic_seed(mnemonic_seed_bytes)

    assert isinstance(keypair, Secp256k1Keypair)
    assert keypair.public_key is not None
    assert isinstance(keypair.public_key, str)
    assert len(keypair.public_key) == 66, f"expected compressed public key length of 66 hex characters, got {len(keypair.public_key)}"