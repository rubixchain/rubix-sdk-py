from dataclasses import dataclass


@dataclass

class RBTBalance:
    """

    Represents the RBT balance details for a user.
    

    Attributes:

        balance (float): RBT balance.

        pledged (float): RBT balance pledged.

        locked (float): RBT balance locked.
    """
    balance: float

    pledged: float
    locked: float


@dataclass

class FTBalance:
    """

    Represents the balance details of a fungible token (FT).
    

    Attributes:
        name (str): Name of the FT
        creator (str): Creator DID of the FT
        value (float): Value of the FT
        count (int): Count of the FT
    """

    name: str
    creator: str
    value: float
    count: int


@dataclass

class SmartContractChain:
    """
    Represents a block of tokens in a smart contract.
    
    Attributes:
        transactionId(str): Transaction ID
        initiator(str): DID of the initiator of the transaction
        epoch(int): Epoch of the transaction
        data(str): Data associated with the transaction
    """
    transactionId: str
    initiator: str
    epoch: int
    data: str

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