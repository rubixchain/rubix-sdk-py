from typing import Optional


class FTInfo:
    def __init__(self, ft_name: str, number_of_fts: float, creator_did: str):
        self.ft_name = ft_name
        self.number_of_fts = number_of_fts
        self.creator_did = creator_did

    def to_json(self):
        return {
            "ftName": self.ft_name,
            "numberOfFts": self.number_of_fts,
            "creatorDID": self.creator_did
        }

class NFTInfo:
    def __init__(self, nft_id: str, value: float, data: str, parentNFTId: str = ""):
        self.nft_id = nft_id
        self.value = value
        self.data = data
        self.parentNFTId = parentNFTId

    def to_json(self):
        return {
            "nftId": self.nft_id,
            "value": self.value,
            "data": self.data,
            "parentNFTId": self.parentNFTId
        }

class SmartContractInfo:
    def __init__(self, smart_contract_id: str, value: float, data: str):
        self.smart_contract_id = smart_contract_id
        self.value = value
        self.data = data

    def to_json(self):
        return {
            "smartContractId": self.smart_contract_id,
            "value": self.value,
            "data": self.data
        }

class TransactionTokenDetails:
    def __init__(
        self,
        rbt: Optional[float] = None,
        ft: Optional[list[FTInfo]] = None,
        nft: Optional[list[NFTInfo]] = None,
        smartContract: Optional[list[SmartContractInfo]] = None,
        transferNftOwnership: bool = False,
    ):
        if rbt is None and ft is None and nft is None and smartContract is None:
            raise ValueError("At least one of rbt, ft, nft, smartContract must be provided")

        self.rbt = rbt
        self.ft = ft
        self.nft = nft
        self.smartContract = smartContract
        self.transferNftOwnership = transferNftOwnership

    def to_json(self):
        return {
            "rbt": self.rbt,
            "ft": [ft.to_json() for ft in self.ft] if self.ft else [],
            "nft": [nft.to_json() for nft in self.nft] if self.nft else [],
            "smartContract": [sc.to_json() for sc in self.smartContract] if self.smartContract else [],
            "transferNftOwnership": self.transferNftOwnership
        }

class TransactionRequest:
    def __init__(self, initiator: str, owner: str, tokens: TransactionTokenDetails, memo: str = ""):
        self.initiator = initiator
        self.owner = owner
        self.tokens = tokens
        self.memo = memo

    def to_json(self):
        return {
            "initiator": self.initiator,
            "owner": self.owner,
            "tokens": self.tokens.to_json(),
            "memo": self.memo
        }
