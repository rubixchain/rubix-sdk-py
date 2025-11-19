from rubix.client import RubixClient
from rubix.signer import Signer
from rubix.querier import Querier

def transfer_rbt_tokens():
    client = RubixClient("<Rubix Node URL>")

    signer = Signer(
        rubixClient=client,
        mnemonic="<Enter 24-word long BIP-39 mnemonic>",
        alias="nero"
    )

    print("Signer DID: ", signer.did)

    response = signer.send_rbt_tokens(
        receiver_did="<Enter recipient DID>",
        rbt_amount=0.001,
        comment="Test RBT Transfer"
    )

    if response["status"] is True:
        print("RBT Transfer Successful!")
    else:
        print("RBT Transfer Failed!: ", response.get("message", ""))

def check_rbt_balance():
    client = RubixClient("<Rubix Node URL>")

    rubixQuerier = Querier(client)
    balance = rubixQuerier.get_rbt_balance("bafybmicbopex4ydytrtremmculwpo7e5p2uvbkuw2ds775xmkcsc5lglai")

    print(f"RBT Balance: {balance['rbt']}")
