import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.builders.pse import LegalIdType, PseBuilder, UserType


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
        return PseBuilder()


def test_pse_builder_sets_payment_method_and_builds_transaction():
    builder = make_builder()
    transaction = (
        builder.amount_in_cents(2500)
        .customer_email("user@example.com")
        .payment_method(
            "1234567",
            "1001",
            "Pago con PSE",
            user_legal_id_type=LegalIdType.NIT,
            user_type=UserType.BUSINESS,
        )
        .build()
    )

    assert transaction.payment_method == {
        "type": "PSE",
        "user_type": 1,
        "user_legal_id_type": "NIT",
        "user_legal_id": "1234567",
        "financial_institution_code": "1001",
        "payment_description": "Pago con PSE",
    }
    assert transaction.payment_method_type == "PSE"
    assert transaction.amount_in_cents == 2500
    assert transaction.customer_email == "user@example.com"


def test_pse_builder_uses_default_enum_values_when_not_provided():
    builder = make_builder()
    transaction = (
        builder.amount_in_cents(3000)
        .customer_email("client@example.com")
        .payment_method("1234567", "1001", "Pago con PSE")
        .build()
    )

    assert transaction.payment_method["user_type"] == UserType.INDIVIDUAL.value
    assert transaction.payment_method["user_legal_id_type"] == LegalIdType.CC.value


def test_pse_builder_requires_legal_id():
    builder = make_builder()

    with pytest.raises(ValueError, match="Legal ID is required"):
        builder.amount_in_cents(2500).customer_email("user@example.com").payment_method("", "1001", "Pago con PSE").build()


def test_pse_builder_requires_legal_id_length_greater_than_six():
    builder = make_builder()

    with pytest.raises(ValueError, match="The length of your legal ID must be greater than 6"):
        builder.amount_in_cents(2500).customer_email("user@example.com").payment_method("123456", "1001", "Pago con PSE").build()


def test_pse_builder_validates_legal_id_type_length():
    builder = make_builder()
    builder.amount_in_cents(2500).customer_email("user@example.com").payment_method("1234567", "1001", "Pago con PSE")
    builder._transaction.payment_method["user_legal_id_type"] = "ABCD"

    with pytest.raises(ValueError, match="The type of legal ID is not valid"):
        builder.build()


def test_pse_builder_keeps_shared_transaction_validation():
    with pytest.raises(ValueError, match="Amount is required"):
        make_builder().amount_in_cents(0).customer_email("user@example.com").payment_method("1234567", "1001", "Pago con PSE").build()

    with pytest.raises(ValueError, match="Email is required"):
        make_builder().amount_in_cents(2500).payment_method("1234567", "1001", "Pago con PSE").build()
