import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.builders.credit_card import CreditCardBuilder


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def make_builder():
    with patch("src.schemas.requests.get") as mock_get:
        mock_get.return_value = DummyResponse(
            {
                "data": {
                    "presigned_acceptance": {"acceptance_token": "acceptance-123"},
                    "presigned_personal_data_auth": {"acceptance_token": "auth-456"},
                }
            }
        )
        os.environ["BASE_URL"] = "https://example.com"
        os.environ["PUBLIC_KEY"] = "public-key"
        return CreditCardBuilder()


def test_credit_card_builder_sets_payment_method_and_builds_transaction():
    builder = make_builder()
    transaction = (
        builder.amount_in_cents(1500)
        .customer_email("user@example.com")
        .payment_method("tok_card_123", 3)
        .build()
    )

    assert transaction.payment_method == {
        "type": "CARD",
        "token": "tok_card_123",
        "installments": 3,
    }
    assert transaction.payment_method_type == "CARD"
    assert transaction.amount_in_cents == 1500
    assert transaction.customer_email == "user@example.com"


def test_credit_card_builder_requires_token():
    builder = make_builder()

    with pytest.raises(ValueError, match="Token is required"):
        builder.amount_in_cents(1500).customer_email("user@example.com").payment_method("").build()


def test_credit_card_builder_keeps_shared_transaction_validation():
    with pytest.raises(ValueError, match="Amount is required"):
        make_builder().amount_in_cents(0).customer_email("user@example.com").payment_method("tok_card_123").build()

    with pytest.raises(ValueError, match="Email is required"):
        make_builder().amount_in_cents(1500).payment_method("tok_card_123").build()
