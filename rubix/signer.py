import base64
import os

from pathlib import Path
from .client import RubixClient
from .crypto.bip39 import generate_bip39_mnemonic, get_seed_from_mnemonic
from .crypto.secp256k1 import Secp256k1Keypair
from .did import create_did
from .crypto.account import save_account_to_file, load_account_from_file
from .utils.validate import validate_asset_address
from .models.tx import TransactionRequest, TransactionTokenDetails, SmartContractInfo, FTInfo, NFTInfo

CONFIG_ACCOUNTS_DIR = "account"

class Signer:
    """
    Signer provides abstraction for user keys management
    """
    def __init__(self, rubixClient: RubixClient, alias: str, mnemonic: str = "", config_path: str = "",
                 passphrase: str = "mypassword"):
        """
        Initializes Signer instance.

        Args:
            rubixClient (RubixClient): An instance of RubixClient for API interactions.
            alias (str): Alias for Rubix Account.
            mnemonic (str, optional): 24-word mnemonic phrase for key generation or import. Defaults to "".
            config_path (str, optional): SDK config path. Defaults to "" 
                        and internally is set to <HOME_DIR>/.rubix_sdk.
            passphrase (str, optional): Passphrase for encrypting/decrypting the private key. 
                        Defaults to "mypassword". It is HIGHLY RECOMMENDED to provide a passphrase
        """
        # Set config path
        self.__config_path = ""
        if config_path == "":
            home_dir = Path.home()
            default_config_path =  os.path.join(home_dir, ".rubix_sdk")
            self.__config_path = default_config_path
        else:
            self.__config_path = config_path

        # Set Rubix Client
        if rubixClient is None:
            raise ValueError("RubixClient instance is required")
        self.__client: RubixClient = rubixClient

        # Check if alias has been provided for their account
        if alias == "":
            raise ValueError("alias must be provided to initiate Signer")
        
        complete_account_dir = os.path.join(self.__config_path, CONFIG_ACCOUNTS_DIR)
        
        # If the alias directory doesn't exists, create it with keypair. The keypair
        # could either come from a mnemonic or be newly generated.
        complete_key_path = os.path.join(complete_account_dir, alias)
        if not os.path.exists(complete_key_path):
            # Get the secp256k1 keypair from mnemonic
            if mnemonic == "":
                mnemonic_str = generate_bip39_mnemonic()
                if mnemonic_str is None or mnemonic_str.strip() == "":
                    raise ValueError("Failed to generate mnemonic phrase.")           
                self.__mnemonic = mnemonic_str
            else:
                self.__mnemonic = mnemonic

            seed = get_seed_from_mnemonic(self.__mnemonic)
            self.__keypair = Secp256k1Keypair.from_mnemonic_seed(seed)

            # Request DID creation from Rubix node
            created_did = create_did(self.__keypair, self.__client.node_url)
            if created_did is None or created_did.strip() == "":
                raise ValueError("Failed to create DID from mnemonic seed.")
            
            self.did = created_did
            self.quorum_type = 2
            
            # Save keys to config file
            save_account_to_file(
                account_dir=complete_account_dir,
                public_key=bytes.fromhex(self.__keypair.public_key),
                private_key=bytes.fromhex(self.__keypair.private_key),
                did=self.did,
                alias=alias,
                passphrase=passphrase
            )
        else:
            # Load keys from config file
            rubixAcccount = load_account_from_file(
                account_dir=complete_account_dir,
                alias=alias,
                passphrase=passphrase
            )
            self.__keypair = rubixAcccount.keypair
            self.did = rubixAcccount.did
            self.quorum_type = 2
            self.__mnemonic = ""

    def __quorum_type(self) -> int:
        """Returns the quorum type for transaction"""
        return 2


    def __signature_response(self, id: str, message_hash: bytes):
        """Sends signature response to Rubix node
        
        Args:
            id (str): Transaction request ID.
            message_hash (bytes): The message hash.
            
        Returns:
            Response from the Rubix node.
        """
        signature_bytes = self.__keypair.sign(message_hash)

        signature_response_body = {
            "id": id,
            "signature": base64.b64encode(signature_bytes).decode("utf-8")
        }

        response = self.__client._make_post_request(
            "/rubix/v1/signature",
            signature_response_body
        )

        if response["result"] is None or type(response["result"]["transactionID"]) is str:
            return response
        else:
            new_message_hash = base64.b64decode(response["result"]["hash"])
            new_request_id = response["result"]["id"]
            return self.__signature_response(new_request_id, new_message_hash)

    def __generate_smart_contract_address(self, user_did: str, wasm_file: str, code_file: str) -> str:
        """
        Generates smart contract address by uploading necessary files to Rubix node.

        Args:
            user_did: The DID of the user deploying the smart contract.
            wasm_file: Path to the WASM file.
            code_file: Path to the code file.

        Returns:
            str: Smart contract address
        
        Raises:
            FileNotFoundError: If any of the specified files do not exist.
            Exception: If the Rubix node returns an error or empty result.
        """
        if not os.path.exists(wasm_file):
            raise FileNotFoundError(f"WASM file not found: {wasm_file}")
        
        if not os.path.exists(code_file):
            raise FileNotFoundError(f"Code file not found: {code_file}")
        
        with open(wasm_file, "rb") as wasm_f, open(code_file, "rb") as code_f:
            files = {
                "binaryCodePath": (os.path.basename(wasm_file), wasm_f),
                "rawCodePath": (os.path.basename(code_file), code_f),
            }

            data = {
                "did": user_did
            }
        
            response = self.__client._make_form_data_request(
                endpoint="/rubix/v1/smart_contracts/generate",
                files=files,
                data=data
            )

            if response["status"] is False:
                raise Exception(f"Smart contract hash generation failed: {response['message']}")
            
            if response["result"] == "":
                raise Exception("Empty smart contract hash received from Rubix node. err: ", response["message"])
            
            return response["result"]

    def __generate_nft_address(self, user_did: str, artifact_file: str, metadata_file: str) -> str:
        """
        Generates NFT address

        Args:
            user_did: The DID of the user deploying the NFT.
            artifact_file: Path to the artifact file.
            metadata_file: Path to the metadata file.
            
        Returns:
            str: NFT address

        Raises:
            FileNotFoundError: If any of the specified files do not exist.
            Exception: If the Rubix node returns an error or empty result.
        """
        if not os.path.exists(artifact_file):
            raise FileNotFoundError(f"Artifact file not found: {artifact_file}")

        if not os.path.exists(metadata_file):
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        with open(artifact_file, "rb") as artifact_f, open(metadata_file, "rb") as metadata_f:
            files = {
                "artifact": (os.path.basename(artifact_file), artifact_f),
                "metadata": (os.path.basename(metadata_file), metadata_f)
            }

            data = {
                "did": user_did
            }

            response = self.__client._make_form_data_request(
                endpoint="/rubix/v1/nfts/generate",
                files=files,
                data=data
            )

            if response["status"] is False:
                raise Exception(f"NFT address generation failed: {response['message']}")

            if response["result"] == "":
                raise Exception("Empty NFT address received from Rubix node. err: ", response["message"])

            return response["result"]

    def get_mnemonic(self) -> str:
        """Returns the mnemonic phrase associated with the signer."""
        return self.__mnemonic
    
    def get_keypair(self) -> Secp256k1Keypair:
        """Returns the Secp256k1 keypair associated with the signer."""
        return self.__keypair
    
    def init_tx(self, request: TransactionRequest):
        """Initiates a transaction

        Args:
            request (TransactionRequest): The transaction request.

        Returns:
            Transaction response from the Rubix node.
        """

        tx_response = self.__client._make_post_request(
            "/rubix/v1/tx",
            json_data=request.to_json()
        )

        request_id = tx_response["result"]["id"]
        request_hash = base64.b64decode(tx_response["result"]["hash"])
        
        tx_response = self.__signature_response(request_id, request_hash)
        
        # Return the final response
        return tx_response

    def send_rbt_tokens(self, receiver_did: str, rbt_amount: float, memo: str = ""):
        """Send RBT tokens

        Args:
            receiver_did (str): The DID of the receiver.
            rbt_amount (float): The amount of RBT tokens to send.
            memo (str, optional): An optional memo for the transaction. Defaults to "".

        Returns:
           Transaction response from the Rubix node.
        """
        tx_request = TransactionRequest(
            initiator=self.did,
            owner=receiver_did,
            tokens=TransactionTokenDetails(
                rbt=rbt_amount,
            ),
            memo=memo
        )

        tx_response = self.init_tx(tx_request)
        
        # Return the final response
        return tx_response

    def create_ft(self, name: str, supply: int, rbt_lock_amount: int):
        """
        Creates a new FT token
        
        Args:
            name (str): The name of the FT.
            supply (int): The total supply of the FT.
            rbt_lock_amount (int): The amount of RBT tokens to lock for FT creation.

        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the FT creation initiation fails.    
        """

        tx_body = {
            "did": self.did,
            "ft_count": supply,
            "ft_name": name,
            "ft_num_start_index": 0,
            "token_count": rbt_lock_amount
        }

        create_ft_response = self.__client._make_post_request(
            endpoint="/rubix/v1/fts/mint",
            json_data=tx_body
        )

        if create_ft_response["status"] is False:
            raise Exception(f"FT creation initiation failed: {create_ft_response['message']}")

        # Sign the transaction
        request_id = create_ft_response["result"]["id"]
        request_hash = base64.b64decode(create_ft_response["result"]["hash"])
        
        tx_response = self.__signature_response(request_id, request_hash)
        
        # Return the final response
        return tx_response

    def send_ft(self, receiver_did: str, ft_name: str, ft_count: int, ft_creator_did: str, comment: str = ""):
        """
        Sends FT tokens

        Args:
            receiver_did (str): The DID of the receiver.
            ft_name (str): The name of the FT.
            ft_count (int): The amount of FT tokens to send.
            ft_creator_did (str): The DID of the FT creator.
            comment (str, optional): An optional comment for the transaction. Defaults to "".

        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the FT transfer initiation fails.
        """

        tx_body = TransactionRequest(
            initiator=self.did,
            owner=receiver_did,
            tokens=TransactionTokenDetails(
                ft=[
                    FTInfo(
                        ft_name=ft_name,
                        number_of_fts=ft_count,
                        creator_did=ft_creator_did
                    )
                ]
            ),
            memo=comment
        )

        tx_response = self.init_tx(tx_body)

        # Return the final response
        return tx_response
    
    def deploy_smart_contract(self, wasm_file: str, code_file: str, contract_value: float, smart_contract_data: str, comment: str = ""):
        """
        Deploys a smart contract

        Args:
            wasm_file (str): Path to the WASM file.
            code_file (str): Path to the code file.
            contract_value (float): Amount of RBT tokens to lock for contract deployment.
            comment (str, optional): An optional comment for the transaction.

        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the smart contract deployment fails.
        """
        deployer_did = self.did
        smart_contract_address = self.__generate_smart_contract_address(deployer_did, wasm_file, code_file)

        tx_body = TransactionRequest(
            initiator=self.did,
            owner="",
            tokens=TransactionTokenDetails(
                smartContract=[
                    SmartContractInfo(
                        smart_contract_id=smart_contract_address,
                        value=contract_value,
                        data=smart_contract_data
                    )
                ]
            ),
            memo=comment
        )

        tx_response = self.init_tx(tx_body)

        # Return the final response
        if tx_response["status"] is True:
            return {
                "contract_address": smart_contract_address,
            }
        else:
            return {
                "error": tx_response.get("message", "Unknown error during smart contract deployment.")
            }

    def execute_smart_contract(self, contract_address: str, smart_contract_data: str, comment: str = ""):
        """
        Executes a smart contract
        
        Args:
            contract_address (str): The address of the smart contract to execute.
            comment (str, optional): An optional comment for the transaction.
            smart_contract_data (str): Arbitrary data for the smart contract execution.

        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the smart contract execution fails.
        """
        tx_body = TransactionRequest(
            initiator=self.did,
            owner="",
            tokens=TransactionTokenDetails(
                smartContract=[
                    SmartContractInfo(
                        smart_contract_id=contract_address,
                        value=0,
                        data=smart_contract_data
                    )
                ]
            ),
            memo=comment
        )

        tx_response = self.init_tx(tx_body)
        
        # Return the final response
        return tx_response

    def deploy_nft(self, nft_data: str, nft_value: float, artifact_file: str = "", metadata_file: str = "", nft_id: str = ""):
        """
        Deploys an NFT

        Args:
            artifact_file (str, optional): Path to the artifact file.
            metadata_file (str, optional): (To be Deprecated) Path to the metadata file.
            nft_data (str): Arbitrary data for the NFT.
            nft_value (float): The value of the NFT.
            nft_metadata_info (str, optional): Additional metadata information for the NFT. Defaults to "".
            nft_file_name (str, optional): Name of the NFT file. Defaults to "".
            nft_id (str, optional): Pre-computed IPFS CID v0. If this is passed, then `metadata_file` and
                           and `artifact_file` are ignored

        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the NFT deployment fails.
        """
        deployer_did = self.did

        # Either nft_id or both artifact_file and metadata_file should be passed.
        # Passing all of them or none of them would result in an error
        if nft_id != "" and artifact_file != "" and metadata_file != "":
            raise AttributeError("values for `nft_id`, `artifact_file` and `metadata_file` have been passed. " \
            " Either pass `nft_id` or both `artifact_file` and `metadata_file`")
        
        if nft_id == "" and artifact_file == "" and metadata_file == "":
            raise AttributeError("`nft_id`, `artifact_file` and `metadata_file` are empty. " \
            " Either pass `nft_id` or both `artifact_file` and `metadata_file`")

        if nft_id == "":
            nft_address = self.__generate_nft_address(
                user_did=deployer_did,
                artifact_file=artifact_file,
                metadata_file=metadata_file
            )
        else:
            # validate nft_id
            if not validate_asset_address(nft_id):
                raise ValueError(f"nft_id passed is not in a valid format, value: {nft_id}")

            nft_address = nft_id

        tx_body = TransactionRequest(
            initiator=self.did,
            owner="",
            tokens=TransactionTokenDetails(
                nft=[
                    NFTInfo(
                        nft_id=nft_address,
                        value=nft_value,
                        data=nft_data
                    )
                ]
            ),
            memo=""
        )

        tx_response = self.init_tx(tx_body)

        # Return the final response
        if tx_response["status"] is True:
            return {
                "nft_address": nft_address,
            }
        else:
            return {
                "error": tx_response.get("message", "Unknown error during NFT deployment.")
            }

    def execute_nft(self, nft_address: str, nft_data: str, nft_value: float = 1, comment: str = ""):
        """
        Executes an NFT
        
        Args:
            nft_address (str): The address of the NFT to execute.
            comment (str, optional): An optional comment for the transaction.
            nft_data (str): Arbitrary data for the NFT execution.

        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the NFT execution fails.
        """
        tx_body = TransactionRequest(
            initiator=self.did,
            owner=self.did,
            tokens=TransactionTokenDetails(
                nft=[
                    NFTInfo(
                        nft_id=nft_address,
                        value=nft_value,
                        data=nft_data
                    )
                ]
            ),
            memo=comment
        )

        tx_response = self.init_tx(tx_body)

        # Return the final response
        return tx_response

    def create_child_nft(self, parent_nft_address: str, nft_data: str = "", nft_value: float = 0.0, comment: str = ""):
        """
        Creates a child NFT of an existing NFT

        Args:
            parent_nft_address (str): The address of the parent NFT.
            nft_data (str): Arbitrary data for the child NFT.
            nft_value (float, optional): The value of the child NFT. Defaults to 0.0.
            comment (str, optional): An optional comment for the transaction. Defaults to "".

        Returns:
            Success response with child NFT address if the transaction is successful, otherwise error response.

        Raises:
            Exception: If the child NFT creation fails.
        """
        tx_body = TransactionRequest(
            initiator=self.did,
            owner=self.did,
            tokens=TransactionTokenDetails(
                nft=[
                    NFTInfo(
                        nft_id=parent_nft_address,
                        value=nft_value,
                        data=nft_data,
                        parentNFTId=parent_nft_address
                    )
                ]
            ),
            memo=comment
        )

        tx_response = self.init_tx(tx_body)
        if tx_response["status"] is True:
            try:
                child_nft_address = tx_response["result"]["mintedNFTChildren"]
            except KeyError as e:
                raise Exception("Child NFT address not found in the transaction response.") from e
            return {
                "child_nfts": child_nft_address
            }
        else:
            return {
                "error": tx_response.get("message", "Unknown error during child NFT creation.")
            }

    def transfer_nft(self, nft_address: str, receiver_did: str, nft_value: float, nft_data: str = "", comment: str = ""):
        """
        Transfers NFT ownership to another DID

        Args:
            nft_address (str): The address of the NFT to transfer.
            receiver_did (str): The DID of the receiver.
            nft_value (float): The value of the NFT.
            nft_data (str, optional): Additional data for the NFT. Defaults to "".
            comment (str, optional): An optional comment for the transaction. Defaults to "".
        
        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the NFT ownership transfer fails.
        """
        tx_body = TransactionRequest(
            initiator=self.did,
            owner=receiver_did,
            tokens=TransactionTokenDetails(
                nft=[
                    NFTInfo(
                        nft_id=nft_address,
                        value=nft_value,
                        data=nft_data
                    )
                ]
            ),
            memo=comment
        )

        tx_response = self.init_tx(tx_body)

        # Return the final response
        return tx_response