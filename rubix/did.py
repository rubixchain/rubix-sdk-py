import base64
import requests

from .crypto.secp256k1 import Secp256k1Keypair
from urllib.parse import urlparse, urljoin

class DIDCreationError(Exception):
    """Raised when DID creation fails."""
    pass

class DIDRegistrationError(Exception):
    """Raised when DID registration fails."""
    pass

class signatureResponseError(Exception):
    """Raised when signature response fails."""
    pass

# TODO: To be deprecated once the creation of DID is implemented on the 
# 0x address scheme is implemented on RubixCore
# Creation of DID will become a method of Signer class
def create_did(keypair: Secp256k1Keypair, rubixNodeBaseUrl: str) -> None:
    request_did_api_url = urlparse(rubixNodeBaseUrl)
    if all([request_did_api_url.scheme, request_did_api_url.netloc]):
        pass

    # Create IPFS based DID 
    request_did_api_url = urljoin(rubixNodeBaseUrl, "/api/request-did-for-pubkey")

    public_key = keypair.public_key
    if public_key is None or public_key.strip() == "":
        raise ValueError("Public key is required to create DID")

    try:
        response = requests.post(
            request_did_api_url,
            json={"public_key": public_key},
            timeout=300
        )
        response.raise_for_status() 
        
    except requests.exceptions.Timeout:
        raise DIDCreationError("Request to Rubix node timed out")
    except requests.exceptions.ConnectionError:
        raise DIDCreationError(f"Failed to connect to Rubix node at {rubixNodeBaseUrl}")
    except requests.exceptions.HTTPError as e:
        raise DIDCreationError(f"HTTP error from Rubix node: {e}")
    except requests.exceptions.RequestException as e:
        raise DIDCreationError(f"Request failed: {e}")
    
    try:
        response_body = response.json()
    except ValueError:
        raise DIDCreationError("Invalid JSON response from Rubix node")
    
    if "status" in response_body and response_body["status"] is False:
        raise DIDCreationError(f"DID creation failed: {response_body['message']}")

    user_did = response_body["did"]

    # Register the newly created DID
    register_did_url = urljoin(rubixNodeBaseUrl, "/api/register-did")

    try:
        response = requests.post(
            register_did_url,
            json={"did": user_did},
            timeout=300
        )
        response.raise_for_status() 
        
    except requests.exceptions.Timeout:
        raise DIDRegistrationError("Request to Rubix node timed out")
    except requests.exceptions.ConnectionError:
        raise DIDRegistrationError(f"Failed to connect to Rubix node at {rubixNodeBaseUrl}")
    except requests.exceptions.HTTPError as e:
        raise DIDRegistrationError(f"HTTP error from Rubix node: {e}")
    except requests.exceptions.RequestException as e:
        raise DIDRegistrationError(f"Request failed: {e}")
    
    try:
        response_body = response.json()
    except ValueError:
        raise DIDRegistrationError("Invalid JSON response from Rubix node")
    
    if "status" in response_body and response_body["status"] is False:
        raise DIDRegistrationError(f"DID registeration failed: {response_body['message']}")
    
    # Retrieve the message from response and sign
    message = response_body["result"]["hash"]

    if message is None or message.strip() == "":
        raise DIDRegistrationError("No message to sign for DID registration")

    # Decode and sign the message
    message_bytes = base64.b64decode(message)

    signature_bytes = keypair.sign(message_bytes)

    # Send the signature-response request
    signature_response_url = urljoin(rubixNodeBaseUrl, "/api/signature-response")
    req_id = response_body["result"]["id"]

    signature_response_body = {
        "id": req_id,
        "Signature": {
            "Signature": list(map(int, signature_bytes))
        },
        "mode": 4
    }

    try:
        response = requests.post(
            signature_response_url,
            json=signature_response_body,
            timeout=300
        )
        response.raise_for_status() 
        
    except requests.exceptions.Timeout:
        raise signatureResponseError("Request to Rubix node timed out")
    except requests.exceptions.ConnectionError:
        raise signatureResponseError(f"Failed to connect to Rubix node at {rubixNodeBaseUrl}")
    except requests.exceptions.HTTPError as e:
        raise signatureResponseError(f"HTTP error from Rubix node: {e}")
    except requests.exceptions.RequestException as e:
        raise signatureResponseError(f"Request failed: {e}")
    
    try:
        response_body = response.json()
    except ValueError:
        raise signatureResponseError("Invalid JSON response from Rubix node")

    if response_body.get("status") is False:
        raise signatureResponseError(f"Signature response failed: {response_body['message']}")

    return user_did

def online_signature_verify(rubixNodeBaseUrl: str, did: str, message: bytes, signature: bytes) -> bool:
    """
    Verifies a signature using Rubix node's online verification service.
    
    Args:
        rubixNodeBaseUrl (str): Base URL of the Rubix node.
        did (str): The DID of the signer.
        message (bytes): The original message that was signed.
        signature (bytes): The signature to verify.
        
    Returns:
        bool: True if signature is valid, False otherwise.
    """

    verify_signature_url = urljoin(rubixNodeBaseUrl, "/api/verify-signature")

    verify_signature_body = {
        "signer_did": did,
        "signed_msg": message.decode('utf-8'),
        "signature": signature.hex()
    }

    try:
        response = requests.get(
            verify_signature_url,
            params=verify_signature_body,
            timeout=300
        )

        response.raise_for_status() 
        
        response_body = response.json()
        return response_body.get("status", False)
    except requests.exceptions.Timeout:
        raise signatureResponseError("Request to Rubix node timed out")
    except requests.exceptions.ConnectionError:
        raise signatureResponseError(f"Failed to connect to Rubix node at {rubixNodeBaseUrl}")
    except requests.exceptions.HTTPError as e:
        raise signatureResponseError(f"HTTP error from Rubix node: {e}")
    except requests.exceptions.RequestException as e:
        raise signatureResponseError(f"Request failed: {e}")
