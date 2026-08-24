from rubix.did import online_signature_verify
from rubix.signer import Signer
from rubix.client import RubixClient

def test_online_verify_valid_signature():
    """Test verifying a valid signature using an online verification service."""
    node_url = "https://chain-connector-2-dev.rubix.net"
    client = RubixClient(node_url)
    
    signer = Signer(
        rubixClient=client,
        alias="martin",
        mnemonic="buffalo tumble defy laundry call almost little pig lift party property pool frame erosion mind library sample floor ring enemy word enemy foster ill"
    )

    signer_did = signer.did

    message = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit."

    signature = signer.get_keypair().sign(message)

    is_valid = online_signature_verify(
        rubixNodeBaseUrl=node_url,
        did=signer_did,
        message=message,
        signature=signature
    )
    assert is_valid is True