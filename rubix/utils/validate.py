from cid import make_cid, CIDv1

def validate_did(did: str, is_ipfs: bool = False) -> bool:
    """
    Validate the format of a DID (Decentralized Identifier).

    Args:
        did (str): The DID string to validate.
        is_ipfs (bool): If True, validate as an IPFS-based CID v1.

    Returns:
        bool: True if the DID is valid, False otherwise.
    """

    is_ipfs = True #TODO: To be removed once non-IPFS DIDs are supported

    if is_ipfs:
        try:
            cid = make_cid(did)
            return cid.version == 1
        except Exception:
            return False
    else:
        return True #TODO: validation logic for upcoming non-IPFS to be added once Core supports it
    
def validate_asset_address(address: str) -> bool:
    """
    Validate the format of an asset address. The asset address format
    is expected to follow IPFS CIDv0 conventions.

    Args:
        address (str): The asset address string to validate.

    Returns:
        bool: True if the asset address is valid, False otherwise.
    """
    try:
        cid = make_cid(address)
        return cid.version == 0
    except Exception:
        return False