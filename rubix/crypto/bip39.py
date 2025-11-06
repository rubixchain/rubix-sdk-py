from mnemonic import Mnemonic

def generate_bip39_mnemonic() -> str:
    """Generate a 24-word BIP39 mnemonic phrase.
    
    Returns:
        str: The generated BIP39 24-word mnemonic phrase.
    """ 
    
    return Mnemonic("english").generate(strength=256)

def get_seed_from_mnemonic(mnemonic_phrase: str, passphrase: str = "") -> bytes:
    """Derive a seed from a BIP39 mnemonic phrase.

    Args:
        mnemonic (str): The BIP39 mnemonic phrase.
        passphrase (str): An optional passphrase to enhance security. Default is an empty string.
    
    Returns:
        bytes: The derived seed in bytes.
    """
    if mnemonic_phrase is None or mnemonic_phrase.strip() == "":
        raise ValueError("Mnemonic phrase cannot be empty.")

    if not Mnemonic("english").check(mnemonic_phrase):
        raise ValueError(f"Invalid mnemonic phrase: {mnemonic_phrase}")

    if len(mnemonic_phrase.split()) != 24:
        raise ValueError(f"Mnemonic phrase must be 24 words long, got {len(mnemonic_phrase.split())}.")

    return Mnemonic("english").to_seed(mnemonic_phrase, passphrase=passphrase)