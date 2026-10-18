import pytest
from pydantic import ValidationError
from governance.contracts.order_event import OrderContract

def test_order_contract_valid():
    payload = {
        "event_id": "evt-999",
        "timestamp": "2026-10-17T12:00:00Z",
        "customer_id": "cust-999",
        "amount": 100.0,
        "currency": "USD"
    }
    contract = OrderContract(**payload)
    assert contract.event_id == "evt-999"
    assert contract.amount == 100.0

def test_order_contract_invalid_amount():
    payload = {
        "event_id": "evt-ERR",
        "timestamp": "2026-10-17T12:00:00Z",
        "customer_id": "cust-999",
        "amount": -50.0,
        "currency": "USD"
    }
    with pytest.raises(ValidationError):
        OrderContract(**payload)
