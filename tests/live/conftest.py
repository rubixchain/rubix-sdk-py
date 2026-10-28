"""
Live tests run against a real Rubix node and need:

- RUBIX_TEST_MNEMONIC: 24-word mnemonic of a funded account (tests needing it are skipped otherwise)
- RUBIX_TEST_DID: optional, the DID expected for that mnemonic
- RUBIX_TEST_RECEIVER_DID: optional, the DID that receives transfers. Defaults to a "receiver"
  account created once in the test config directory
- RUBIX_NODE_URL: optional, defaults to the dev node

Run them with: pytest tests/live
"""
import json
import os
import secrets
import time

import pytest

from rubix.client import RubixClient
from rubix.signer import Signer

NODE_URL = os.environ.get("RUBIX_NODE_URL", "https://chain-connector-2-dev.rubix.net")
FUNDED_MNEMONIC = os.environ.get("RUBIX_TEST_MNEMONIC", "")
FUNDED_DID = os.environ.get("RUBIX_TEST_DID", "")
RECEIVER_DID = os.environ.get("RUBIX_TEST_RECEIVER_DID", "")

# Accounts created by the live tests are kept here (instead of ~/.rubix_sdk) and reused across runs
CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".rubix_sdk_test"))

requires_funded_account = pytest.mark.skipif(
    FUNDED_MNEMONIC == "", reason="RUBIX_TEST_MNEMONIC is not set"
)


def pytest_configure(config):
    config.addinivalue_line("markers", "live: tests that run against a live Rubix node")


def nonce() -> str:
    """A unique value, so that every run deploys assets with fresh addresses."""
    return f"{int(time.time() * 1000)}-{secrets.token_hex(6)}"


@pytest.fixture(scope="session")
def client() -> RubixClient:
    return RubixClient(NODE_URL)


@pytest.fixture(scope="session")
def funded_signer(client) -> Signer:
    if FUNDED_MNEMONIC == "":
        pytest.skip("RUBIX_TEST_MNEMONIC is not set")
    return Signer(rubixClient=client, alias="funded", mnemonic=FUNDED_MNEMONIC, config_path=CONFIG_PATH)


@pytest.fixture(scope="session")
def receiver_did(client) -> str:
    """
    The DID that receives transfers: RUBIX_TEST_RECEIVER_DID, or else an account with a newly
    generated mnemonic, created once and then reused.
    """
    if RECEIVER_DID != "":
        return RECEIVER_DID
    return Signer(rubixClient=client, alias="receiver", config_path=CONFIG_PATH).did


@pytest.fixture
def contract_files(tmp_path):
    """A minimal valid WASM module (with a nonce in a custom section) and a matching source file."""
    name = b"nonce"
    payload = nonce().encode()
    section = bytes([len(name)]) + name + payload
    wasm = b"\x00asm\x01\x00\x00\x00" + bytes([0x00, len(section)]) + section

    wasm_file = tmp_path / "contract.wasm"
    code_file = tmp_path / "contract.rs"
    wasm_file.write_bytes(wasm)
    code_file.write_text(f"// rubix-py live test contract {nonce()}\nfn main() {{}}\n")
    return str(wasm_file), str(code_file)


@pytest.fixture
def nft_files(tmp_path):
    """A small artifact and metadata file for an NFT."""
    artifact_file = tmp_path / "artifact.txt"
    metadata_file = tmp_path / "metadata.json"
    artifact_file.write_text(f"rubix-py live test artifact {nonce()}\n")
    metadata_file.write_text(json.dumps({"name": "rubix-py live test", "nonce": nonce()}))
    return str(artifact_file), str(metadata_file)
