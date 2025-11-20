Rubix Client SDK for Python
============================

``rubix-py`` is a lightweight client for the Rubix Blockchain Node, providing complete node interaction with minimal overhead.

⚠️ This project is currently under **active development**. API changes and method signature updates may occur between releases. Please review the **Release Notes** before upgrading.

Installation
============

Run the following to install ``rubix-py``

.. code-block:: shell

   pip install rubix-py


Architecture
============

The architecture of ``rubix-py`` is pretty straightforward. It consists of the following classes:

- ``RubixClient``: Responsible for connection to Rubix Blockchain Node
- ``Signer``: Signs and performs Blockchain transactions and manages user's crypto keys.
- ``Querier``: Queries information such as Token Balances, Smart Contract and NFT token chains, etc.

``RubixClient`` has a set of internal methods to make API requests to the node. Both ``Signer`` and ``Querier`` consumes an instance of ``RubixClient`` which helps them to achieve their respective operations with the Blockchain node.

Let's have a look at a simple example of fetching RBT balance and transferring them:

.. code-block:: python

   from rubix.client import RubixClient
   from rubix.signer import Signer
   from rubix.querier import Querier

   # Define the RubixClient by specifying the target Rubix node address
   # and optionally providing timeout in seconds
   client = RubixClient(node_url="http://localhost:20000", timeout=300)

   # The Singer class takes two mandatory inputs:
   # - rubixClient: Rubix Client instance
   # - alias: Alias give to the account holding the cryptographic keypair. It can therefore
   # be used everytime user wants to refer to the same keypair present in SDK config. If the
   # keypair files are not present, it will be created. The keypair values will then depend on
   # whether user passes a mnemonic or not 
   #
   # Optional Arguments:
   # - mnemonic: Account can be recovered by passing a 24-word BIP-39 mnemonic. If not passed,
   # a random mnemonic is generated.
   # - config_path: Directory where files associated with SDK such as keypairs will be stored
   signer = Signer(
        rubixClient=client,
        alias="nick",
        mnemonic="<Enter 24-word long BIP-39 mnemonic>",
        config_path="<Config Path for SDK dir>"
    )


   # Internally, a call is made to Rubix Node to create and register your DID
   user_did = signer.did

   # Retrieve the keypair which can be used for signing arbitrary message
   keypair = signer.get_keypair()

   # Retrieve the mnemonic
   mnemonic = signer.get_mnemonic()

   # Define the Querier
   queryClient = Querier(
       rubixClient=client
   )

   # Check RBT balance
   balance_info = queryClient.get_rbt_balance(user_did)
   balance = balance_info["rbt"]

   # Perform RBT Transfer
   tx_response = signer.send_rbt_tokens(
       receiver_did="<Enter recipient DID>",
       rbt_amount=0.001,
       comment="Test RBT Transfer"
   )

   if tx_response["status"] is True:
       print("RBT Transfer Successful!")
   else:
       print("RBT Transfer Failed!: ", tx_response.get("message", ""))


Usage
=====

Refer `examples <https://github.com/your-org/rubix-py/tree/main/examples>`_ for more usecases
