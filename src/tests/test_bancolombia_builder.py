import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.builders.bancolombia import (
    BancolombiaBuilder,
    BancolombiaQrBuilder,
    SandboxStatus,
)


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
        return BancolombiaBuilder()


def make_qr_builder():
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
        return BancolombiaQrBuilder()


def test_bancolombia_builder_sets_payment_method_and_builds_transaction():
    builder = make_builder()
    transaction = (
        builder.amount_in_cents(2500)
        .customer_email("user@example.com")
        .payment_method("Compra online", "https://example.com/checkout")
        .build()
    )

    assert transaction.payment_method == {
        "type": "BANCOLOMBIA_TRANSFER",
        "user_type": "PERSON",
        "payment_description": "Compra online",
        "ecommerce_url": "https://example.com/checkout",
    }
    assert transaction.payment_method_type == "BANCOLOMBIA_TRANSFER"
    assert transaction.payment_method_user_type == "PERSON"
    assert transaction.amount_in_cents == 2500
    assert transaction.customer_email == "user@example.com"


def test_bancolombia_builder_sets_user_type_and_builds_transaction():
    builder = make_builder()
    transaction = (
        builder.amount_in_cents(2500)
        .customer_email("user@example.com")
        .payment_method("Compra online", "https://example.com/checkout")
        .build()
    )

    assert transaction.payment_method["user_type"] == "PERSON"
    assert transaction.payment_method["type"] == "BANCOLOMBIA_TRANSFER"


def test_bancolombia_qr_builder_sets_payment_method_and_uses_enum_status():
    builder = make_qr_builder()
    transaction = (
        builder.amount_in_cents(1800)
        .customer_email("user@example.com")
        .payment_method("Pago QR", SandboxStatus.DECLINED)
        .build()
    )

    assert transaction.payment_method == {
        "type": "BANCOLOMBIA_QR",
        "payment_description": "Pago QR",
        "sandbox_status": "DECLINED",
    }
    assert transaction.payment_method_type == "BANCOLOMBIA_QR"
    assert transaction.amount_in_cents == 1800
    assert transaction.customer_email == "user@example.com"


def test_bancolombia_qr_builder_requires_description():
    builder = make_qr_builder()

    with pytest.raises(ValueError, match="Description is required"):
        builder.amount_in_cents(1800).customer_email("user@example.com").payment_method("").build()


def test_bancolombia_builders_keep_shared_transaction_validation():
    with pytest.raises(ValueError, match="Amount is required"):
        make_builder().amount_in_cents(0).customer_email("user@example.com").payment_method("Compra online", "https://example.com/checkout").build()

    with pytest.raises(ValueError, match="Email is required"):
        make_qr_builder().amount_in_cents(1800).payment_method("Pago QR", SandboxStatus.APPROVED).build()
