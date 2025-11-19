import os

from rubix.client import RubixClient
from rubix.signer import Signer
from rubix.querier import Querier

def smart_contract_deployment():
    client = RubixClient("<Rubix Node URL>")

    signer = Signer(
        rubixClient=client,
        mnemonic="<Enter 24-word long BIP-39 mnemonic>",
        alias="nero"
        
    )

    print("Signer DID: ", signer.did)

    response = signer.deploy_smart_contract(
        wasm_file=os.path.join(os.getcwd(), "wasm_file.wasm"),
        code_file=os.path.join(os.getcwd(), "code_file.rs"),
        schema_file=os.path.join(os.getcwd(), "schema_file.json"),
        contract_value=0.001,
    )

    if response.get("error") is not None:
        print("NFT Deployment Failed!: ", response.get("error", ""))
    else:
        print("NFT Address: ", response["contract_address"])

def smart_contract_execution():
    client = RubixClient("<Rubix Node URL>")

    signer = Signer(
        rubixClient=client,
        mnemonic="<Enter 24-word long BIP-39 mnemonic>",
        alias="nero"
    )

    print("Signer DID: ", signer.did)

    response = signer.execute_smart_contract(
        contract_address="<Smart Contract Address>",
        smart_contract_data="test1"
    )

    if response["status"] is False:
        print("Smart Contract Execution Failed!: ", response.get("message", ""))
    else:
        print("Smart Contract Execution Successful, response: ", response)