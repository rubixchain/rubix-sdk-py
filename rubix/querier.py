from .client import RubixClient
from .utils.validate import validate_did, validate_asset_address

class Querier:
    def __init__(self, rubixClient: RubixClient) -> None:
        # Set Rubix Client
        if rubixClient is None:
            raise ValueError("RubixClient instance is required")
        
        self.__client: RubixClient = rubixClient

    def get_rbt_balance(self, did: str):
        """
        Retrieves the RBT balance for a given DID.
        
        Args:
            did (str): User DID
            
        Returns:
            Returns the RBT balance associated with the DID.
            Conforms to *models.querier.RBTBalance*

        Raises:
            ValueError: If the DID is invalid or if the request fails.
        """
        if not validate_did(did):
            raise ValueError(f"Invalid DID: {did}")

        response = self.__client._make_get_request(
            endpoint="/api/get-account-info",
            params={
                "did": did
            }
        )

        if response["status"] is False:
            raise ValueError(f"Failed to get RBT balance: {response['message']}")

        try:
            account_info = response["account_info"][0]
        except (IndexError, KeyError):
            raise ValueError(f"Invalid account information received, response value: {response}")
        
        rbt_balance = account_info.get("rbt_amount", 0)

        return {
            "did": did,
            "rbt": rbt_balance
        }
    
    def get_ft_balances(self, did: str):
        """
        Retrieves the FT balances for a given DID.
        
        Args:
            did (str): User DID
            
        Returns:
            A list of FTBalance objects containing FT details.
            Conforms to List of *models.querier.FTBalance*
            
        Raises:
            ValueError: If the DID is invalid or if the request fails.
            KeyError: If the expected data is not found in the response.
            IndexError: If the response structure is not as expected.
        """
        if not validate_did(did):
            raise ValueError(f"Invalid DID: {did}")

        response = self.__client._make_get_request(
            endpoint="/api/get-ft-info-by-did",
            params={
                "did": did
            }
        )

        if response["status"] is False:
            raise ValueError(f"Failed to get FT balances: {response['message']}")

        try:
            ft_balance_list = response["ft_info"]
            return ft_balance_list
        except (IndexError, KeyError):
            raise ValueError(f"Invalid account information received, response value: {response}")

    def get_smart_contract_states(
            self, contract_address: str, 
            only_latest_state: bool = False
        ):
        """
        Retrieves the states of a smart contract by its address.
        
        Args:
            contract_address (str): The address of the smart contract.
            only_latest_state (bool): Whether to retrieve only the latest state of the Smart Contract.
                                      Default is False.
        Returns:
            A list containing the smart contract states. 
            Conforms to list of models.querier.SmartContractTokenBlock

        Raises:
            ValueError: If the contract address is invalid or if the request fails.
        """
        if not validate_asset_address(contract_address):
            raise ValueError(f"Invalid smart contract address: {contract_address}")

        response = self.__client._make_post_request(
            endpoint="/api/get-smart-contract-token-chain-data",
            json_data={
                "latest": only_latest_state,
                "token": contract_address
            }
        )

        if response["status"] is False:
            raise ValueError(f"Failed to get smart contract states: {response['message']}")

        if response["SCTDataReply"] is None:
            raise ValueError(f"No smart contract states found for address: {contract_address}")

        try:
            smart_contract_states = response["SCTDataReply"]
            return smart_contract_states
        except KeyError:
            raise ValueError(f"Invalid contract information received, response value: {response}")
        
    def get_nft_states(self, nft_address: str, only_latest_state: bool = False):
        """
        Retrieves the states of an NFT by its address.
        
        Args:
            nft_address (str): The address of the NFT.
            only_latest_state (bool): Whether to retrieve only the latest state of the NFT.
                                      Default is False.
        
        Returns:
            List containing the NFT states.
            Conforms to List of *models.querier.NFTTokenBlock*
        
        Raises:
            ValueError: If the NFT address is invalid or if the request fails.
        """
        if not validate_asset_address(nft_address):
            raise ValueError(f"Invalid NFT address: {nft_address}")

        response = self.__client._make_get_request(
            endpoint="/api/get-nft-token-chain-data",
            params={
                "latest": only_latest_state,
                "nft": nft_address
            }
        )

        if response["status"] is False:
            raise ValueError(f"Failed to get NFT states: {response['message']}")

        if response["NFTDataReply"] is None:
            raise ValueError(f"No NFT states found for address: {nft_address}")

        try:
            nft_states= response["NFTDataReply"]
            return nft_states
        except KeyError:
            raise ValueError(f"Invalid NFT information received, response value: {response}")

    def get_all_nft(self):
        """
        Retrieves all NFTs present in a Rubix Subnet

        Returns:
            List containing information about all NFTs.
            Conforms to List of *models.querier.NFTInfo*
        """

        response = self.__client._make_get_request(
            endpoint="/api/list-nfts"
        )

        if response["status"] is False:
            raise ValueError(f"Failed to get all NFTs: {response['message']}")

        try:
            nft_list = response["nfts"]
            return nft_list
        except KeyError:
            raise ValueError(f"Invalid NFT information received, response value: {response}")
    
    def get_nfts_by_owner(self, owner_did: str):
        """
        Retrieves all NFTs owned by a specific DID.
        
        Args:
            owner_did (str): The DID of the owner.
        
        Returns:
            List containing information about NFTs owned by the specified DID.
            Conforms to List of *models.querier.NFTInfo*
        
        Raises:
            ValueError: If the DID is invalid or if the request fails.
        """
        if not validate_did(owner_did):
            raise ValueError(f"Invalid DID: {owner_did}")

        response = self.__client._make_get_request(
            endpoint="/api/get-nfts-by-did",
            params={
                "did": owner_did
            }
        )

        if response["status"] is False:
            raise ValueError(f"Failed to get NFTs by owner: {response['message']}")

        try:
            nft_list = response["nfts"]
            return nft_list
        except KeyError:
            raise ValueError(f"Invalid NFT information received, response value: {response}")