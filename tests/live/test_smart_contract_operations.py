import pytest

from rubix.querier import Querier

from .conftest import requires_funded_account

pytestmark = [pytest.mark.live, requires_funded_account]


# Based on examples/smart_contract_operations.py. The tests depend on each other and run in order,
# sharing what they create through `state`.
@pytest.fixture(scope="module")
def state() -> dict:
    return {}


def test_deploys_a_smart_contract(funded_signer, contract_files, state):
    wasm_file, code_file = contract_files

    response = funded_signer.deploy_smart_contract(
        wasm_file=wasm_file,
        code_file=code_file,
        contract_value=0.001,
        smart_contract_data="",
    )

    assert response.get("error") is None, f"Smart Contract Deployment Failed!: {response.get('error')}"
    contract_address = response["contract_address"]
    assert contract_address.startswith("Qm")
    state["contract_address"] = contract_address


def test_executes_the_smart_contract(client, funded_signer, state):
    if "contract_address" not in state:
        pytest.skip("the smart contract was not deployed")
    contract_address = state["contract_address"]

    response = funded_signer.execute_smart_contract(
        contract_address=contract_address,
        smart_contract_data="test1",
    )

    assert response["status"] is True, f"Smart Contract Execution Failed!: {response.get('message', '')}"

    states = Querier(client).get_smart_contract_states(contract_address)
    assert len(states) > 1
    latest = states[-1]
    assert set(latest) == {"transactionId", "initiator", "epoch", "data"}
    assert latest["initiator"] == funded_signer.did
    assert latest["data"] == "test1"

    assert Querier(client).get_smart_contract_states(contract_address, only_latest_state=True) == [latest]
