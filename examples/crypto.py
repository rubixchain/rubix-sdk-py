from rubix.crypto.secp256k1 import Secp256k1Keypair

def sign_arbitrary_data(data: bytes):
    # Generate a new Secp256k1 keypair
    keypair = Secp256k1Keypair.from_private_key(bytes.fromhex("<private key in hex>"))

    print("Public Key (hex):", keypair.public_key)

    signature_bytes = keypair.sign(data)
