import os
import random
import string
import hashlib
import json
import requests
from abc import ABC, abstractmethod
from requests.models import Response
from dotenv import load_dotenv

load_dotenv()

class MerchantInfo(ABC):
    @abstractmethod
    def presigned_data(self) -> dict:
        ...

class AcceptanceTokens(MerchantInfo):
    def __init__(self):
        self._response = requests.get(f'{os.getenv('BASE_URL')}/merchants/info', headers={'x-merchant-public-key': os.getenv('PUBLIC_KEY')}).json()

    # presigned_acceptance
    # presigned_personal_data_auth
    def presigned_data(self, key: str) -> dict:
        try:
            return self._response['data'][key]
        except requests.exceptions.HTTPError as error:
            return error

######################################################################################################

class Transaction:
    def __init__(self):
        self.acceptance_token = None
        self.accept_personal_auth = None
        self.amount_in_cents = 0
        self.currency = 'COP'
        self.signature = None
        self.customer_email = None
        self.reference = None
        self.payment_method = {}

    def create(self):
        data = {
            'acceptance_token': self.acceptance_token,
            'accept_personal_auth': self.accept_personal_auth,
            'amount_in_cents': self.amount_in_cents,
            'currency': self.currency,
            'signature': self.signature,
            'customer_email': self.customer_email,
            'reference': self.reference,
            'payment_method': self.payment_method
        }
        response = requests.post(f'{os.getenv('BASE_URL')}/transactions', headers={'Authorization': f'Bearer {os.getenv('PRIVATE_KEY')}'}, data=json.dumps(data))
        return response.json()

class CreditCard(Transaction):
    def __init__(self):
        super().__init__()
        self.payment_method_type = 'CARD'
        self.ip = None
        self.redirect_url = None

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

credit_card = CreditCardBuilder()
credit_builder = credit_card.acceptance_token().accept_personal_auth().amount_in_cents(1500000).signature().customer_email('eocc28@hotmail.com').reference().redirect_url('http://localhost:3000/purchase').build()
print(credit_builder.create())
