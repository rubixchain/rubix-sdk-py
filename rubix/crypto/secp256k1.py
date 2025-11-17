import bip32utils

from ecpy.curves import Curve, Point
from ecpy.keys import ECPrivateKey, ECPublicKey
from ecpy.ecdsa import ECDSA
from ecdsa import SigningKey, SECP256k1
from coincurve import PublicKey as CoincurvePublicKey

def secp256k1_sign(private_key: bytes, message: bytes) -> bytes:
    """Signs a message using secp256k1 private key.

    Args:
        private_key (bytes): Secp256k1 private key.
        message (bytes): The message to sign.

    Returns:
        bytes: The generated signature in bytes.
    """
    cv = Curve.get_curve('secp256k1')
    pv_key = ECPrivateKey(int.from_bytes(private_key, 'big'), cv)
    signer = ECDSA()

    sig = signer.sign(message, pv_key)
    if sig is None:
        raise ValueError("Failed to sign the message.")
    
    return bytes(sig)

def secp256k1_verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Verifies secp256k1 signature.

    Args:
        public_key (bytes): Compressed public key.
        message (bytes): The original message that was signed.
        signature (bytes): The signature to verify.

    Returns:
        bool: True if signature is valid, False otherwise.
    """
    cv = Curve.get_curve('secp256k1')

    # check if the public key is in compressed format
    uncompressed_public_key = None
    
    if len(public_key) == 33:
        coincurve_pub_key = CoincurvePublicKey(public_key)
        uncompressed_public_key = coincurve_pub_key.format(compressed=False)
    elif len(public_key) == 65:
        uncompressed_public_key = public_key
    else:
        raise ValueError(f"Invalid public key of length {len(public_key)}.")
    
    # Form public key object
    x = int.from_bytes(uncompressed_public_key[1:33], 'big')
    y = int.from_bytes(uncompressed_public_key[33:], 'big')
    ec_point = Point(x, y, cv)
    pub_key_obj = ECPublicKey(ec_point)

    # Verify signature
    verifier = ECDSA()
    return verifier.verify(message, signature, pub_key_obj)

class Secp256k1Keypair:
    def __init__(self, private_key: str, public_key: str):
        self.__private_key: str = private_key
        self.__public_key: str = public_key

    @staticmethod
    def from_mnemonic_seed(mnemonic_seed: bytes) -> 'Secp256k1Keypair':
        """Generates a Secp256k1Keypair from a mnemonic seed.
        
        Args:
            mnemonic_seed (bytes): The mnemonic seed used to derive the keypair.

        Returns:
            Secp256k1Keypair: The generated Secp256k1 keypair.
        """
        bip32_root_key = bip32utils.BIP32Key.fromEntropy(mnemonic_seed)
        bip32_child_key = bip32_root_key.ChildKey(0)

        if not bip32_child_key:
            raise ValueError("Failed to derive child key from mnemonic seed.")

        private_key = bip32_child_key.PrivateKey()

        return Secp256k1Keypair.from_private_key(private_key)
    
    @staticmethod
    def from_private_key(private_key: bytes) -> 'Secp256k1Keypair':
        """Generates a Secp256k1Keypair from a private key.
        
        Args:
            private_key (bytes): The private key used to derive the keypair.
        Returns:
            Secp256k1Keypair: The generated Secp256k1 keypair.
        """

        signing_key = SigningKey.from_string(private_key, curve=SECP256k1)
        private_key_hex = signing_key.to_string().hex()

        public_key = signing_key.get_verifying_key()
        if not public_key:
            raise ValueError("Failed to derive public key from private key.")
        
    
        public_key_hex = public_key.to_string("compressed").hex()

        return Secp256k1Keypair(private_key_hex, public_key_hex)

    @property
    def public_key(self) -> str:
        """Returns the public key in hexadecimal format."""
        return self.__public_key
    
    def sign(self, message: bytes) -> bytes:
        """Signs a message using secp256k1 private key.

        Args:
            message (bytes): The message to sign.

        Returns:
            bytes: The generated signature in bytes.
        """
        return secp256k1_sign(bytes.fromhex(self.__private_key), message)
