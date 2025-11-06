import pytest
from rubix.crypto.bip39 import generate_bip39_mnemonic, get_seed_from_mnemonic

def test_generate_bip39_mnemonic():
    """Test the generation of a 24-word BIP39 mnemonic phrase."""
    mnemonic = generate_bip39_mnemonic()
    assert isinstance(mnemonic, str)
    assert len(mnemonic.split()) == 24

def test_get_seed_from_mnemonic():
    """Test the extraction of the seed from a BIP39 mnemonic phrase."""
    mnemonic = "buffalo tumble defy laundry call almost little pig lift party property pool frame erosion mind library sample floor ring enemy word enemy foster ill"
    expected_seed_hex = "1884e5ddc2a5fb783f60803868cffaef1af1ce36e6686357c9c5dd6c80b63d698d78a8db3cab0404ecd3d966a00b9d51e4ac783997f78f64a1b24152e09ec524"
    
    seed = get_seed_from_mnemonic(mnemonic)
    assert isinstance(seed, bytes)
    assert len(seed) == 64
    
    actual_seed_hex = seed.hex()
    assert actual_seed_hex == expected_seed_hex
