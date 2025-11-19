import os
import base64
import textwrap
import secrets

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from pathlib import Path

def secp256k1_pubkey_hex_to_pem(file_path: str, public_key_bytes: bytes) -> None:
    """
    secp256k1_to_pem writes the secp256k1 public key to a PEM file.

    Args:
        file_path (str): The path to the PEM file.
        public_key_bytes (bytes): The secp256k1 public key to write.
    """
    if file_path == "":
        raise ValueError("File path must not be empty")
    if public_key_bytes is None:
        raise ValueError("Public key must not be None")
    
    pub_key_file = "pubKey.pem"
    
    b64 = base64.b64encode(public_key_bytes).decode("ascii")
    wrapped = "\n".join(textwrap.wrap(b64, 64))

    pem_text = (
        "-----BEGIN PUBLIC KEY-----\n"
        f"{wrapped}\n"
        "-----END PUBLIC KEY-----\n"
    )

    complete_key_path = os.path.join(file_path, pub_key_file)
    try:
        Path(complete_key_path).write_text(pem_text, encoding="utf-8")
    except Exception as e:
        raise IOError(f"Failed to write public key to a PEM file: {e}")
    

def secp256k1_pubkey_pem_to_hex(filename: str) -> str:
    """
    Extract the compressed secp256k1 public key hex from the PEM file.

    Args:
        filename (str): The path to the PEM file.
    
    Returns:
        str: The compressed secp256k1 public key in hexadecimal format.
    """

    pem = Path(filename).read_text(encoding="utf-8").strip()

    start = "-----BEGIN PUBLIC KEY-----"
    end = "-----END PUBLIC KEY-----"

    if start not in pem or end not in pem:
        raise ValueError("Not a valid PUBLIC KEY PEM.")

    body = pem.split(start)[1].split(end)[0].strip()
    body = "".join(body.split())  # remove whitespace

    try:
        pub_bytes = base64.b64decode(body)
    except:
        raise ValueError("Invalid base64 inside PEM.")

    if len(pub_bytes) != 33 or pub_bytes[0] not in (2, 3):
        raise ValueError("Decoded key is not a compressed secp256k1 key.")

    return pub_bytes.hex()

def _derive_key(passphrase: str, salt: bytes, iterations: int = 200_000) -> bytes:
    """
    Derive a 32-byte key from passphrase + salt using PBKDF2-HMAC-SHA256.
    """
    if not isinstance(passphrase, (bytes, str)):
        raise TypeError("passphrase must be bytes or str")
    if isinstance(passphrase, str):
        passphrase = passphrase.encode("utf-8")
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(passphrase)

def secp256k1_privkey_hex_to_pem(priv_key_dir: str, priv_hex_bytes: bytes, passphrase: str = "mypassword") -> None:
    """
    Encrypt the 32-byte private key (hex string) and write it inside a ENCRYPTED PRIVATE KEY PEM-like block.

    Args:
        priv_hex_bytes: Private Key in bytes
        priv_key_dir: directory path to write PEM
        passphrase: passphrase to encrypt with (default "mypassword")
    """
    if not isinstance(priv_hex_bytes, bytes):
        raise TypeError("priv_hex must be bytes or str")

    priv_hex = priv_hex_bytes.hex()

    priv_hex = priv_hex.strip().lower()
    if len(priv_hex) != 64:
        raise ValueError("Private key hex must be exactly 64 hex characters (32 bytes).")

    try:
        priv_bytes = bytes.fromhex(priv_hex)
    except Exception as e:
        raise ValueError("Invalid private key hex.") from e

    if len(priv_bytes) != 32:
        raise ValueError("Private key must be 32 bytes.")

    # Generate salt and nonce
    salt = secrets.token_bytes(16)      # 16 bytes salt for PBKDF2
    nonce = secrets.token_bytes(12)     # 12 bytes nonce for AESGCM

    # Derive 32-byte key
    key = _derive_key(passphrase, salt)

    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, priv_bytes, associated_data=None)
    # Store: salt || nonce || ciphertext
    stored = salt + nonce + ciphertext

    b64 = base64.b64encode(stored).decode("ascii")
    wrapped = "\n".join(textwrap.wrap(b64, 64))
    pem_text = (
        "-----BEGIN ENCRYPTED PRIVATE KEY-----\n"
        f"{wrapped}\n"
        "-----END ENCRYPTED PRIVATE KEY-----\n"
    )

    complete_priv_key_dir = os.path.join(priv_key_dir, "privKey.pem")
    Path(complete_priv_key_dir).write_text(pem_text, encoding="utf-8")

def secp256k1_privkey_pem_to_hex(filename: str, passphrase: str = "mypassword") -> str:
    """
    Read the PEM written by privhex_to_hex, decrypt with passphrase, and return the private key hex.

    Args:
        filename (str): The path to the PEM file.
        passphrase (str): The passphrase used for decryption (default "mypassword").
    
    Returns:
        str: The decrypted private key in hexadecimal format.
    """
    pem = Path(filename).read_text(encoding="utf-8")
    start = "-----BEGIN ENCRYPTED PRIVATE KEY-----"
    end = "-----END ENCRYPTED PRIVATE KEY-----"

    if start not in pem or end not in pem:
        raise ValueError("PEM does not contain expected ENCRYPTED PRIVATE KEY headers.")

    body = pem.split(start, 1)[1].split(end, 1)[0].strip()
    b64 = "".join(body.split())

    try:
        stored = base64.b64decode(b64)
    except Exception as e:
        raise ValueError("PEM body is not valid base64.") from e

    # Extract salt(16), nonce(12), ciphertext(rest)
    if len(stored) < 16 + 12 + 16:
        # must be at least salt+nonce+tag (tag is 16 bytes for GCM) even if empty ciphertext
        raise ValueError("Stored data is too short to be valid.")

    salt = stored[:16]
    nonce = stored[16:28]
    ciphertext = stored[28:]

    key = _derive_key(passphrase, salt)
    aesgcm = AESGCM(key)
    try:
        priv_bytes = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    except Exception as e:
        raise ValueError("Failed to decrypt private key (wrong passphrase or corrupted data).") from e

    if len(priv_bytes) != 32:
        raise ValueError("Decrypted data is not a 32-byte private key.")

    return priv_bytes.hex()