from .transaction import TransactionBuilder
from src.payment_methods import CreditCard

class CreditCardBuilder(TransactionBuilder):
    def __init__(self):
        super().__init__()
        self._transaction = CreditCard()

    def payment_method(self, token: str, installments: int = 1) -> 'CreditCardBuilder':
        data = { 'type': self._transaction.payment_method_type, 'token': token, 'installments': installments }
        self._transaction.payment_method = data
        return self

    def build(self) -> CreditCard:
        super().build()
        if not self._transaction.payment_method['token']:
            raise ValueError('Token is required')
        return self._transaction