from dataclasses import dataclass

@dataclass
class RBTBalance:
    """
    Represents the RBT balance details for a user.
    
    Attributes:
        did (str): The user's DID.
        rbt (str): The RBT balance associated with the DID.
    """
    did: str
    rbt: str

@dataclass
class FTBalance:
    """
    Represents the balance details of a fungible token (FT).
    
    Attributes:
        ft_name (str): The name of the fungible token.
        ft_count (int): The count of the fungible token.
        creator_did (str): The DID of the creator of the fungible token.
    """
    ft_name: str
    ft_count: int
    creator_did: str

@dataclass
class SmartContractTokenBlock:
    """
    Represents a block of tokens in a smart contract.
    
    Attributes:
        BlockNo (int): The block number.
        BlockId (str): The block ID.
        SmartContractData (str): Arbitrary data provided to the smart contract.
        Epoch (int): The epoch number.
        InitiatorSignature (str): The signature of the initiator.
        ExecutorDID (str): The DID of the executor.
        InitiatorSignData (str): The sign data of the initiator.
    """
    BlockNo: int
    BlockId: str
    SmartContractData: str
    Epoch: int
    InitiatorSignature: str
    ExecutorDID: str
    InitiatorSignData: str

@dataclass
class NFTTokenBlock:
    """
    Represents a block of NFT token
    
    Attributes:
        BlockNo (int): The block number.
        BlockId (str): The block ID.
        NFTData (str): Arbitrary data provided to the NFT.
        NFTOwner (str): The owner of the NFT.
        NFTValue (float): The value of the NFT.
        Epoch (int): Block Epoch.
        TransactionID (str): The transaction ID associated with the NFT.
    """
    BlockNo: int
    BlockId: str
    NFTData: str
    NFTOwner: str
    NFTValue: float
    Epoch: int
    TransactionID: str

@dataclass
class NFTInfo:
    nft: str
    owner_did: str
    nft_value: float
    nft_metadata: str
    nft_file_name: str