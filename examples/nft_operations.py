import os

from rubix.client import RubixClient
from rubix.querier import Querier
from rubix.signer import Signer

def perform_nft_deployment():
    client = RubixClient("<Rubix Node URL>")

    signer = Signer(
        rubixClient=client,
        mnemonic="<Enter 24-word long BIP-39 mnemonic>"
    )

    print("Signer DID: ", signer.did)

    response = signer.deploy_nft(
        artifact_file=os.path.join(os.getcwd(), "artifact_file"),
        metadata_file=os.path.join(os.getcwd(), "metadata_file"),
        nft_value=0.001,
        nft_data="init data"
    )

    if response.get("error") is not None:
        print("NFT Deployment Failed!: ", response.get("error", ""))
    else:
        print("NFT Address: ", response["nft_address"])

def perform_nft_execution():
    client = RubixClient("<Rubix Node URL>")

    signer = Signer(
        rubixClient=client,
        mnemonic="<Enter 24-word long BIP-39 mnemonic>"
    )

    print("Signer DID: ", signer.did)

    response = signer.execute_nft(
        nft_address="<NFT Address>",
        nft_data="test execution data"
    )

    if response["status"] is False:
        print("NFT Execution Failed!: ", response.get("message", ""))
    else:
        print("NFT Execution Successful, response: ", response)

def get_nft_token_chain():
    client = RubixClient("<Rubix Node URL>")

    rubixQuerier = Querier(client)
    states = rubixQuerier.get_nft_states(
        nft_address="<NFT Address>",
        only_latest_state=False # Set True, if only the latest state is needed
    )

    print(f"Total NFT States Retrieved: {states}")

def get_list_of_nfts():
    client = RubixClient("<Rubix Node URL>")

    rubixQuerier = Querier(client)
    nft_list = rubixQuerier.get_all_nft()

    print(f"Total NFTs Retrieved: ", nft_list)

def get_nfts_by_owner_did():
    client = RubixClient("<Rubix Node URL>")

    rubixQuerier = Querier(client)
    nfts = rubixQuerier.get_nfts_by_owner(
        owner_did="<Owner DID>"
    )

    print(f"Total NFTs Retrieved: {nfts}")

