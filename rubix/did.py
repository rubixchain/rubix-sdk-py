import base64
import requests
import os

from .crypto.secp256k1 import Secp256k1Keypair
from urllib.parse import urlparse, urljoin
from .crypto.account import load_pub_key_from_file, save_pub_key_to_file

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
    request_did_api_url = urljoin(rubixNodeBaseUrl, "rubix/v1/dids/create")

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

    user_did = response_body["result"]["did"]

    # Register the newly created DID
    register_did_url = urljoin(rubixNodeBaseUrl, f"/rubix/v1/dids/{user_did}/register")

    try:
        response = requests.post(
            register_did_url,
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
    signature_response_url = urljoin(rubixNodeBaseUrl, "/rubix/v1/signature")
    req_id = response_body["result"]["id"]

    signature_response_body = {
        "id": req_id,
        "signature": base64.b64encode(signature_bytes).decode("utf-8")
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

    verify_signature_url = urljoin(rubixNodeBaseUrl, "/rubix/v1/signature/verify")

    verify_signature_body = {
        "signer_did": did,
        "signed_msg": message.decode('utf-8'),
        "signature": base64.b64encode(signature).decode("utf-8")
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

def get_public_key_for_did(did: str, rubixNodeBaseUrl: str) -> bytes:
    """
    Retrieves the public key associated with a given DID from the Rubix node.
    
    Args:
        did (str): The DID for which to retrieve the public key.
        rubixNodeBaseUrl (str): Base URL of the Rubix node.
        
    Returns:
        str: The public key associated with the DID.
    """
    get_public_key_url = urljoin(rubixNodeBaseUrl, f"/rubix/v1/dids/{did}/public_key")

    try:
        response = requests.get(
            get_public_key_url,
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
        raise DIDCreationError(f"Failed to retrieve public key: {response_body['message']}")

    pub_key_hex = response_body["result"]["public_key"]
    if pub_key_hex is None or pub_key_hex.strip() == "":
        raise DIDCreationError("No public key found for the given DID")

    pub_key_bytes = bytes.fromhex(pub_key_hex)
    return pub_key_bytes

def fast_signature_verify(
    rubixNodeBaseUrl: str, 
    account_dir: str, 
    did: str, 
    message: bytes, 
    signature: bytes
) -> bool:
        """
        Verifies a signature using the public key associated with the DID.
        If the DID is not found in the local configuration, it fetches the 
        public key from the Rubix node and saves it for future use.

        The DID value is considered as the alias while creating the directory
        under accounts directory
        
        Args:
            rubixNodeBaseUrl (str): Base URL of the Rubix node.
            account_dir (str): Directory where DID-related configuration is stored.
            did (str): The DID of the signer.
            message (bytes): The original message that was signed.
            signature (bytes): The signature to verify.

        Returns:
            bool: True if signature is valid, False otherwise.
        """

        from .did import get_public_key_for_did

        # Within accounts dir, scan each alias named folder to see if we find our did
        did_found = False
        did_path = ""

        for alias_folder in os.listdir(account_dir):
            alias_folder_path = os.path.join(account_dir, alias_folder)
            if os.path.isdir(alias_folder_path):
                did_folder_path = os.path.join(alias_folder_path, did)
                if os.path.isdir(did_folder_path):
                    did_found = True
                    did_path = did_folder_path
                    break

        if did_found:
            if not os.path.exists(did_path):
                raise FileNotFoundError(f"Public key file not found for DID {did} at {did_path}")
            public_key = load_pub_key_from_file(did_path)

        else:
            did_path = os.path.join(account_dir, did, did)
            
            # Fetch public key from Rubix node
            public_key = get_public_key_for_did(did, rubixNodeBaseUrl)

            save_pub_key_to_file(
                key_dir=did_path,
                public_key=public_key
            )

        from .crypto.secp256k1 import secp256k1_verify
        return secp256k1_verify(public_key, message, signature)