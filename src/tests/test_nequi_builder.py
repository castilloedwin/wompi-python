import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.builders.nequi import NequiBuilder


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
        return NequiBuilder()


def test_nequi_builder_sets_payment_method_and_builds_transaction():
    builder = make_builder()
    transaction = (
        builder.amount_in_cents(1500)
        .customer_email("user@example.com")
        .payment_method("3001234567")
        .build()
    )

    assert transaction.payment_method == {"type": "NEQUI", "phone_number": "3001234567"}
    assert transaction.payment_method_type == "NEQUI"
    assert transaction.amount_in_cents == 1500
    assert transaction.customer_email == "user@example.com"


def test_nequi_builder_requires_phone_number():
    builder = make_builder()

    with pytest.raises(ValueError, match="Phone number is required"):
        builder.amount_in_cents(1500).customer_email("user@example.com").payment_method("").build()


def test_nequi_builder_requires_exactly_ten_digits():
    builder = make_builder()

    with pytest.raises(ValueError, match="Your phone number must have ten numbers"):
        builder.amount_in_cents(1500).customer_email("user@example.com").payment_method("30012345").build()
