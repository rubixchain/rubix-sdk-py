import base64
import os

from .client import RubixClient
from .crypto.bip39 import generate_bip39_mnemonic, get_seed_from_mnemonic
from .crypto.secp256k1 import Secp256k1Keypair
from .did import create_did

class Signer:
    """
    Singer provides abstraction for user keys management 
    """
    def __init__(self, rubixClient: RubixClient, mnemonic: str = ""):
        # Set Rubix Client
        if rubixClient is None:
            raise ValueError("RubixClient instance is required")
        
        self.__client: RubixClient = rubixClient

        # Set or generate Mnemonic
        self.__mnemonic = ""

        if mnemonic == "":
            mnemonic_str = generate_bip39_mnemonic()
            if mnemonic_str is None or mnemonic_str.strip() == "":
                raise ValueError("Failed to generate mnemonic phrase.")
            
            self.__mnemonic = mnemonic_str
        else:
            self.__mnemonic = mnemonic    

        # Get the secp256k1 keypair from mnemonic
        seed = get_seed_from_mnemonic(self.__mnemonic)
        self.__keypair = Secp256k1Keypair.from_mnemonic_seed(seed)

        did = create_did(self.__keypair, self.__client.node_url)
        if did is None or did.strip() == "":
            raise ValueError("Failed to create DID from mnemonic seed.")
        
        self.did = did
        self.quorum_type = 2

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
            "Signature": {
                "Signature": list(map(int, signature_bytes))
            },
            "mode": 4
        }

        response = self.__client._make_post_request(
            "/api/signature-response", 
            signature_response_body
        )

        if response["result"] is None or type(response["result"]) is str:
            return response
        else:
            new_message_hash = base64.b64decode(response["result"]["hash"])
            new_request_id = response["result"]["id"]
            return self.__signature_response(new_request_id, new_message_hash)

    def __generate_smart_contract_address(self, user_did: str, wasm_file: str, code_file: str, schema_file: str) -> str:
        """
        Generates smart contract address by uploading necessary files to Rubix node.

        Args:
            user_did: The DID of the user deploying the smart contract.
            wasm_file: Path to the WASM file.
            code_file: Path to the code file.
            schema_file: (To be Deprecated) Path to the schema file.
            
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
        
        if not os.path.exists(schema_file):
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(wasm_file, "rb") as wasm_f, open(code_file, "rb") as code_f, open(schema_file, "rb") as schema_f:
            files = {
                "binaryCodePath": (os.path.basename(wasm_file), wasm_f),
                "rawCodePath": (os.path.basename(code_file), code_f),
                "schemaFilePath": (os.path.basename(schema_file), schema_f)
            }

            data = {
                "did": user_did
            }
        
            response = self.__client._make_form_data_request(
                endpoint="/api/generate-smart-contract",
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
                endpoint="/api/create-nft",
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
    
    def send_rbt_tokens(self, receiver_did: str, rbt_amount: float, comment: str = ""):
        """Send RBT tokens

        Args:
            receiver_did (str): The DID of the receiver.
            rbt_amount (float): The amount of RBT tokens to send.
            comment (str, optional): An optional comment for the transaction. Defaults to "".

        Returns:
           Transaction response from the Rubix node.
        """
        tx_body = {
            "comment": comment,
            "receiver": receiver_did,
            "sender": self.did,
            "tokenCOunt": rbt_amount,
            "type": self.__quorum_type()
        }

        rbt_transfer_response = self.__client._make_post_request(
            endpoint="/api/initiate-rbt-transfer",
            json_data=tx_body
        )

        if rbt_transfer_response["status"] is False:
            raise Exception(f"RBT transfer initiation failed: {rbt_transfer_response['message']}")

        # Sign the transaction
        request_id = rbt_transfer_response["result"]["id"]
        request_hash = base64.b64decode(rbt_transfer_response["result"]["hash"])
        
        tx_response = self.__signature_response(request_id, request_hash)
        
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
            endpoint="/api/create-ft",
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

        tx_body = {
            "comment": comment,
            "creatorDID": ft_creator_did,
            "ft_count": ft_count,
            "ft_name": ft_name,
            "quorum_type": self.__quorum_type(),
            "receiver": receiver_did,
            "sender": self.did
        }

        send_ft_response = self.__client._make_post_request(
            endpoint="/api/initiate-ft-transfer",
            json_data=tx_body
        )

        if send_ft_response["status"] is False:
            raise Exception(f"FT transfer initiation failed: {send_ft_response['message']}")

        # Sign the transaction
        request_id = send_ft_response["result"]["id"]
        request_hash = base64.b64decode(send_ft_response["result"]["hash"])

        tx_response = self.__signature_response(request_id, request_hash)

        # Return the final response
        return tx_response
    
    def deploy_smart_contract(self, wasm_file: str, code_file: str, schema_file: str, contract_value: float, comment: str = ""):
        """
        Deploys a smart contract

        Args:
            wasm_file (str): Path to the WASM file.
            code_file (str): Path to the code file.
            schema_file (str): (To be Deprecated) Path to the schema file.
            contract_value (float): Amount of RBT tokens to lock for contract deployment.
            comment (str, optional): An optional comment for the transaction.

        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the smart contract deployment fails.
        """
        deployer_did = self.did
        smart_contract_address = self.__generate_smart_contract_address(deployer_did, wasm_file, code_file, schema_file)

        tx_body = {
            "comment": comment,
            "deployerAddr": deployer_did,
            "quorumType": self.__quorum_type(),
            "rbtAmount": contract_value,
            "smartContractToken": smart_contract_address
        }

        deploy_contract_response = self.__client._make_post_request(
            endpoint="/api/deploy-smart-contract",
            json_data=tx_body
        )

        if deploy_contract_response["status"] is False:
            raise Exception(f"Smart contract deployment failed: {deploy_contract_response['message']}")

        # Sign the transaction
        request_id = deploy_contract_response["result"]["id"]
        request_hash = base64.b64decode(deploy_contract_response["result"]["hash"])

        tx_response = self.__signature_response(request_id, request_hash)

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
        executor_did = self.did
        
        tx_body = {
            "comment": comment,
            "executorAddr": executor_did,
            "quorumType": self.__quorum_type(),
            "smartContractData": smart_contract_data,
            "smartContractToken": contract_address
        }

        contract_execute_response = self.__client._make_post_request(
            endpoint="/api/execute-smart-contract",
            json_data=tx_body
        )

        if contract_execute_response["status"] is False:
            raise Exception(f"Smart contract execution failed: {contract_execute_response['message']}")

        # Sign the transaction
        request_id = contract_execute_response["result"]["id"]
        request_hash = base64.b64decode(contract_execute_response["result"]["hash"])
        
        tx_response = self.__signature_response(request_id, request_hash)
        
        # Return the final response
        return tx_response

    def deploy_nft(self, artifact_file: str, metadata_file: str, nft_data: str, nft_value: float,
                   nft_metadata_info: str = "", nft_file_name: str = ""):
        """
        Deploys an NFT

        Args:
            artifact_file (str): Path to the artifact file.
            metadata_file (str): (To be Deprecated) Path to the metadata file.
            nft_data (str): Arbitrary data for the NFT.
            nft_value (float): The value of the NFT.
            nft_metadata_info (str, optional): Additional metadata information for the NFT. Defaults to "".
            nft_file_name (str, optional): Name of the NFT file. Defaults to "".

        Returns:
            Transaction response from the Rubix node.

        Raises:
            Exception: If the NFT deployment fails.
        """
        deployer_did = self.did
        
        nft_address = self.__generate_nft_address(
            user_did=deployer_did,
            artifact_file=artifact_file,
            metadata_file=metadata_file
        )

        tx_body = {
            "did": deployer_did,
            "nft": nft_address,
            "nft_data": nft_data,
            "nft_file_name": nft_file_name,
            "nft_metadata": nft_metadata_info,
            "nft_value": nft_value,
            "quorum_type": self.__quorum_type()
        }

        deploy_nft_response = self.__client._make_post_request(
            endpoint="/api/deploy-nft",
            json_data=tx_body
        )

        if deploy_nft_response["status"] is False:
            raise Exception(f"NFT deployment failed: {deploy_nft_response['message']}")

        # Sign the transaction
        request_id = deploy_nft_response["result"]["id"]
        request_hash = base64.b64decode(deploy_nft_response["result"]["hash"])

        tx_response = self.__signature_response(request_id, request_hash)

        # Return the final response
        if tx_response["status"] is True:
            return {
                "nft_address": nft_address,
            }
        else:
            return {
                "error": tx_response.get("message", "Unknown error during NFT deployment.")
            }

    def execute_nft(self, nft_address: str, nft_data: str, comment: str = ""):
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
        executor_did = self.did
        
        tx_body = {
            "comment": comment,
            "executor": executor_did,
            "nft": nft_address,
            "nft_data": nft_data,
            "quorum_type": self.__quorum_type(),
            "receiver": ""
        }

        nft_execute_response = self.__client._make_post_request(
            endpoint="/api/execute-nft",
            json_data=tx_body
        )

        if nft_execute_response["status"] is False:
            raise Exception(f"NFT execution failed: {nft_execute_response['message']}")

        # Sign the transaction
        request_id = nft_execute_response["result"]["id"]
        request_hash = base64.b64decode(nft_execute_response["result"]["hash"])
        
        tx_response = self.__signature_response(request_id, request_hash)
        
        # Return the final response
        return tx_response
    
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
        executor_did = self.did
        
        tx_body = {
            "comment": comment,
            "executor": executor_did,
            "nft": nft_address,
            "nft_data": nft_data,
            "nft_value": nft_value,
            "quorum_type": self.__quorum_type(),
            "receiver": receiver_did
        }

        nft_execute_response = self.__client._make_post_request(
            endpoint="/api/execute-nft",
            json_data=tx_body
        )

        if nft_execute_response["status"] is False:
            raise Exception(f"NFT ownership transfer failed: {nft_execute_response['message']}")

        # Sign the transaction
        request_id = nft_execute_response["result"]["id"]
        request_hash = base64.b64decode(nft_execute_response["result"]["hash"])
        
        tx_response = self.__signature_response(request_id, request_hash)
        
        # Return the final response
        return tx_response