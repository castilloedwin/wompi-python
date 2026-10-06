from .transaction import TransactionBuilder
from src.payment_methods import DaviPlata

class DaviPlataBuilder(TransactionBuilder):
    def __init__(self):
        super().__init__()
        self._transaction = DaviPlata()

    def payment_method(self, user_legal_id: str, payment_description: str) -> 'DaviPlataBuilder':
        data = { 'type': self._transaction.payment_method_type, 'user_legal_id_type': self._transaction.payment_method_document_type, 'user_legal_id': user_legal_id, 'payment_description': payment_description }
        self._transaction.payment_method = data
        return self

    def build(self) -> DaviPlata:
        super().build()
        if not self._transaction.payment_method['user_legal_id']:
            raise ValueError('Your personal ID is required')
        return self._transaction