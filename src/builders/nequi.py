from .transaction import TransactionBuilder
from src.payment_methods import Nequi

class NequiBuilder(TransactionBuilder):
    def __init__(self):
        super().__init__()
        self._transaction = Nequi()

    def payment_method(self, phone_number: str) -> 'NequiBuilder':
        data = { 'type': self._transaction.payment_method_type, 'phone_number': phone_number }
        self._transaction.payment_method = data
        return self

    def build(self) -> Nequi:
        super().build()
        if not self._transaction.payment_method['phone_number']:
            raise ValueError('Phone number is required')
        if not len(self._transaction.payment_method['phone_number']) == 10:
            raise ValueError('Your phone number must have ten numbers')
        return self._transaction