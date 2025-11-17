from rubix.client import RubixClient
from rubix.signer import Signer
from rubix.crypto.secp256k1 import Secp256k1Keypair, secp256k1_verify

def sign_and_verify_arbitrary_data(data: bytes):
    # Generate a new Secp256k1 keypair
    client = RubixClient("<Rubix Node URL>")

    signer = Signer(
        rubixClient=client,
        mnemonic="<Enter 24-word long BIP-39 mnemonic>"
    )

    print("Public Key (hex): ", signer.get_keypair().public_key)
    keypair = signer.get_keypair()

    signature_bytes = keypair.sign(data)

    is_valid = secp256k1_verify(bytes.fromhex(keypair.public_key), data, signature_bytes)
    print("Is the signature valid?: ", is_valid)
