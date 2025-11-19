import os

from dataclasses import dataclass
from .pem import secp256k1_pubkey_hex_to_pem, secp256k1_privkey_hex_to_pem, \
    secp256k1_privkey_pem_to_hex, secp256k1_pubkey_pem_to_hex
from .secp256k1 import Secp256k1Keypair

@dataclass
class RubixAccount:
    """
    Abstraction for accounts on Rubix
    """
    did: str
    keypair: Secp256k1Keypair

# TODO: Use RubixAccount type param
def save_account_to_file(account_dir: str, public_key: bytes, private_key: bytes, 
                         did: str, alias: str, passphrase: str = "mypassword") -> None:
    alias_dir = os.path.join(account_dir, alias)

    if not os.path.exists(alias_dir):
        os.makedirs(alias_dir)
    else:
        if not os.path.exists(alias_dir):
            raise FileNotFoundError(f"alias directory does not exist: {alias_dir}")

        alias_subdir = [
            d for d in os.listdir(alias_dir)
            if os.path.isdir(os.path.join(alias_dir, d))
        ]

        if len(alias_subdir) == 1:
            raise FileExistsError(f"cannot create a key directory since one key directory already exists")

        if len(alias_subdir) > 1:
            raise Exception(f"unexpected error: there seems to be multiple DID directories under alias_dir,"
                            f"hence unable to proceed with key creation or import")

    key_dir = os.path.join(alias_dir, did)
    if not os.path.exists(key_dir):
        os.makedirs(key_dir)

    save_key_to_file(key_dir, public_key, private_key, passphrase=passphrase)

def save_key_to_file(key_dir: str, public_key: bytes, private_key: bytes, 
                        passphrase: str = "mypassword") -> None:
    """
    save_account_to_file saves the Rubix Account in a configuration file.

    Args:
        account_dir (str): The path to the configuration file.
        public_key (bytes): The public key to save.
        private_key (bytes): The private key to save.
        did (str): The DID associated with the keys.
        passphrase (str, optional): Passphrase for encrypting the private key. Defaults to
    """

    if public_key is None or len(public_key) == 0:
        raise ValueError("Public key must not be empty")
    if private_key is None or len(private_key) == 0:
        raise ValueError("Private key must not be empty")
    if key_dir == "":
        raise ValueError("Config path must not be empty")

    secp256k1_pubkey_hex_to_pem(key_dir, public_key)
    secp256k1_privkey_hex_to_pem(key_dir, private_key, passphrase=passphrase)

def load_account_from_file(account_dir: str, alias: str, passphrase: str = "mypassword") -> RubixAccount:
    alias_dir = os.path.join(account_dir, alias)
    if not os.path.exists(alias_dir):
        raise FileNotFoundError(f"alias directory does not exist: {alias_dir}")

    alias_subdir = [
        d for d in os.listdir(alias_dir)
        if os.path.isdir(os.path.join(alias_dir, d))
    ]

    if len(alias_subdir) != 1:
        raise ValueError(f"Expected one subdirectory in {alias_dir}, found {len(alias_subdir)}.")

    did = alias_subdir[0]

    key_dir_path = os.path.join(alias_dir, did)
    keypair = load_key_from_file(key_dir_path, passphrase=passphrase)

    return RubixAccount(
        did=did,
        keypair=keypair
    )

def load_key_from_file(key_dir: str, passphrase: str = "mypassword") -> Secp256k1Keypair:
    """
    load_account_from_file loads the Secp256k1 keypair and DID from a configuration file.

    Args:
        key_dir (str): The path to the Keypair files.
        alias (str): The alias associated with the keys.
        passphrase (str, optional): Passphrase for decrypting the private key. Defaults to
            "mypassword".

    Returns:
        Secp256k1Keypair: The loaded keypair.
    """

    if key_dir == "":
        raise ValueError("Config path must not be empty")
    
    if not os.path.exists(key_dir):
        raise FileNotFoundError(f"Key directory does not exist: {key_dir}")

    pub_key_path = os.path.join(key_dir, "pubKey.pem")
    priv_key_path = os.path.join(key_dir, "privKey.pem")

    pub_hex = secp256k1_pubkey_pem_to_hex(pub_key_path)
    priv_hex = secp256k1_privkey_pem_to_hex(priv_key_path, passphrase=passphrase)

    return Secp256k1Keypair(
        private_key=priv_hex,
        public_key=pub_hex
    )
