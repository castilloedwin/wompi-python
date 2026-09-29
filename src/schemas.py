import os
import requests
from abc import ABC, abstractmethod

class MerchantInfo(ABC):
    @abstractmethod
    def presigned_data(self) -> dict:
        ...

class AcceptanceTokens(MerchantInfo):
    def __init__(self):
        self._response = requests.get(f'{os.getenv('BASE_URL')}/merchants/info', headers={'x-merchant-public-key': os.getenv('PUBLIC_KEY')}).json()

    def presigned_data(self, key: str) -> dict:
        try:
            return self._response['data'][key]
        except requests.exceptions.HTTPError as error:
            return error

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
        return data