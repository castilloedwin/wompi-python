import hashlib
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.builders.transaction import TransactionBuilder


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
        return TransactionBuilder()


def test_builder_sets_all_transaction_fields_and_signature():
    os.environ["INTEGRITY_KEY"] = "integrity-secret"
    builder = make_builder()

    transaction = (
        builder.acceptance_token()
        .accept_personal_auth()
        .amount_in_cents(1000)
        .currency("USD")
        .customer_email("user@example.com")
        .reference("REF-123")
        .redirect_url("https://example.com/callback")
        .signature()
        ._transaction
    )

    assert transaction.acceptance_token == "acceptance-123"
    assert transaction.accept_personal_auth == "auth-456"
    assert transaction.amount_in_cents == 1000
    assert transaction.currency == "USD"
    assert transaction.customer_email == "user@example.com"
    assert transaction.reference == "REF-123"
    assert transaction.redirect_url == "https://example.com/callback"

    expected_signature = hashlib.sha256(
        "REF-1231000USDintegrity-secret".encode("utf-8")
    ).hexdigest()
    assert transaction.signature == expected_signature
    assert builder.build() is transaction


def test_reference_generates_fifteen_character_alphanumeric_id_by_default():
    builder = make_builder()

    reference = builder.reference()._transaction.reference

    assert len(reference) == 15
    assert reference.isalnum()


def test_build_validates_required_amount_and_email():
    with pytest.raises(ValueError, match="Amount is required"):
        make_builder().amount_in_cents(0).customer_email("customer@example.com").build()

    with pytest.raises(ValueError, match="Email is required"):
        make_builder().amount_in_cents(5000).build()
