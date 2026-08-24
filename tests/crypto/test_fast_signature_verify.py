import hashlib

from rubix.did import fast_signature_verify
from rubix.signer import Signer
from rubix.client import RubixClient

def test_online_verify_valid_signature_positive():
    """Test verifying a valid signature using an online verification service."""
    node_url = "https://chain-connector-2-dev.rubix.net"
    client = RubixClient(node_url)
    
    signer = Signer(
        alias="jacob",
        rubixClient=client,
    )

    signer_did = "bafybmifxxg6xvzbu6cd5gqrtsl4mqizlnjioz6djp45kq6lq6fn7hl3cmq"

    signature = bytes.fromhex("304402201a656c550f637acf227c4f94d264d9373791bfcacdad5f72818b96f04299849e022003eb085b4d5eecc8df9c651db826ceacb88a48beaf820b23da8fd92bb024afa9")

    message = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    message_hash = hashlib.sha256(message).digest()

    is_valid = fast_signature_verify(
        rubixNodeBaseUrl=node_url,
        account_dir=signer.account_dir,
        did=signer_did,
        message=message_hash,
        signature=signature
    )

    assert is_valid is True

def test_online_verify_valid_signature_negative():
    """Test verifying a valid signature using an online verification service."""
    node_url = "https://chain-connector-2-dev.rubix.net"
    client = RubixClient(node_url)
    
    signer = Signer(
        alias="jacob",
        rubixClient=client,
    )

    signer_did = "bafybmifxxg6xvzbu6cd5gqrtsl4mqizlnjioz6djp45kq6lq6fn7hl3cmq"

    signature = bytes.fromhex("304402201a656c550f637acf227c4f94d264d9373791bfcacdad5f72818b96f04299849e022003eb085b4d5eecc8df9c651db826ceacb88a48beaf820b23da8fd92bb024afa9")

    message = b"Lorem ipsum dolor sit amet, consectetur adipiscing"
    message_hash = hashlib.sha256(message).digest()

    is_valid = fast_signature_verify(
        rubixNodeBaseUrl=node_url,
        account_dir=signer.account_dir,
        did=signer_did,
        message=message_hash,
        signature=signature
    )

    assert is_valid is False