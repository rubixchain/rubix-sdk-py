from rubix.client import RubixClient
from rubix.signer import Signer
from rubix.querier import Querier

def perform_ft_token_transfer():
    client = RubixClient("<Rubix Node URL>")

    signer = Signer(
        rubixClient=client,
        mnemonic="<Enter 24-word long BIP-39 mnemonic>"
    )

    print("Signer DID: ", signer.did)

    response = signer.send_ft(
        receiver_did="<Enter recipient DID>",
        ft_name="ABC",
        ft_count=5,
        ft_creator_did="<Enter FT Creator DID>",
        comment="Test FT Transfer"
    )

    if response["status"] is True:
        print("FT Transfer Successful!")
    else:
        print("FT Transfer Failed!: ", response.get("message", ""))

def check_ft_balances():
    client = RubixClient("<Rubix Node URL>")

    rubixQuerier = Querier(client)
    balances = rubixQuerier.get_ft_balances("bafybmicbopex4ydytrtremmculwpo7e5p2uvbkuw2ds775xmkcsc5lglai")

    if len(balances) == 0:
        print("No FT Balances Found.")
    else:
        print("FT Balances: ", balances)