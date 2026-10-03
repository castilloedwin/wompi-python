import os
import random
import string
import hashlib

from src.schemas import AcceptanceTokens, Transaction

class TransactionBuilder:
    def __init__(self):
        self._transaction = Transaction()
        self._acceptance = AcceptanceTokens()

    def acceptance_token(self) -> 'TransactionBuilder':
        token = self._acceptance.presigned_data('presigned_acceptance')['acceptance_token']
        self._transaction.acceptance_token = token
        return self

    def accept_personal_auth(self) -> 'TransactionBuilder':
        token = self._acceptance.presigned_data('presigned_personal_data_auth')['acceptance_token']
        self._transaction.accept_personal_auth = token
        return self

    def amount_in_cents(self, amount: int) -> 'TransactionBuilder':
        self._transaction.amount_in_cents = amount
        return self

    def currency(self, currency_code: str) -> 'TransactionBuilder':
        self._transaction.currency = currency_code
        return self

    def signature(self) -> 'TransactionBuilder':
        signature = f'{self._transaction.reference}{self._transaction.amount_in_cents}{self._transaction.currency}{os.getenv('INTEGRITY_KEY')}'
        hashed_signature = hashlib.sha256()
        hashed_signature.update(bytes(signature.encode('utf-8')))
        self._transaction.signature = hashed_signature.hexdigest()
        return self

    def customer_email(self, email: str) -> 'TransactionBuilder':
        self._transaction.customer_email = email
        return self

    def reference(self, reference: str = '') -> 'TransactionBuilder':
        if not reference:
            characters = string.ascii_letters + string.digits
            length = 15
            self._transaction.reference = ''.join(random.choices(characters, k=length))
        else:
            self._transaction.reference = reference
        return self

    def redirect_url(self, url: str) -> 'TransactionBuilder':
        self._transaction.redirect_url = url
        return self

    def build(self) -> Transaction:
        if self._transaction.amount_in_cents < 1:
            raise ValueError('Amount is required')
        if not self._transaction.customer_email:
            raise ValueError('Email is required')
        return self._transaction