import os
import random
import string
import hashlib

from src.payment_methods import CreditCard
from src.schemas import AcceptanceTokens

class CreditCardBuilder:
    def __init__(self):
        self._transaction = CreditCard()
        self._acceptance = AcceptanceTokens()

    def acceptance_token(self) -> 'CreditCardBuilder':
        token = self._acceptance.presigned_data('presigned_acceptance')['acceptance_token']
        self._transaction.acceptance_token = token
        return self

    def accept_personal_auth(self) -> 'CreditCardBuilder':
        token = self._acceptance.presigned_data('presigned_personal_data_auth')['acceptance_token']
        self._transaction.accept_personal_auth = token
        return self

    def amount_in_cents(self, amount: int) -> 'CreditCardBuilder':
        self._transaction.amount_in_cents = amount
        return self

    def currency(self, currency_code: str) -> 'CreditCardBuilder':
        self._transaction.currency = currency_code
        return self

    def signature(self) -> 'CreditCardBuilder':
        signature = f'{self._transaction.reference}{self._transaction.amount_in_cents}{self._transaction.currency}{os.getenv('INTEGRITY_KEY')}'
        hashed_signature = hashlib.sha256()
        hashed_signature.update(bytes(signature.encode('utf-8')))
        self._transaction.signature = hashed_signature.hexdigest()
        return self

    def customer_email(self, email: str) -> 'CreditCardBuilder':
        self._transaction.customer_email = email
        return self

    def reference(self, reference: str = '') -> 'CreditCardBuilder':
        if not reference:
            characters = string.ascii_letters + string.digits
            length = 15
            self._transaction.reference = ''.join(random.choices(characters, k=length))
        else:
            self._transaction.reference = reference
        return self

    def redirect_url(self, url: str) -> 'CreditCardBuilder':
        self._transaction.redirect_url = url
        return self

    def build(self):
        if self._transaction.amount_in_cents < 1:
            raise ValueError('Amount is required')
        if not self._transaction.customer_email:
            raise ValueError('Email is required')
        return self._transaction