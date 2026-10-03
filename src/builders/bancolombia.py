from enum import Enum
from .transaction import TransactionBuilder
from src.payment_methods import Bancolombia, BancolombiaQr

class SandboxStatus(Enum):
    APPROVED = 'APPROVED'
    DECLINED = 'DECLINED'
    ERROR = 'ERROR'

class BancolombiaBuilder(TransactionBuilder):
    def __init__(self):
        super().__init__()
        self._transaction = Bancolombia()

    def payment_method(self, payment_description: str, ecommerce_url: str) -> 'BancolombiaBuilder':
        data = { 'type': self._transaction.payment_method_type, 'user_type': self._transaction.payment_method_user_type, 'payment_description': payment_description, 'ecommerce_url': ecommerce_url }
        self._transaction.payment_method = data
        return self

    def build(self) -> Bancolombia:
        super().build()
        if not self._transaction.payment_method['user_type']:
            raise ValueError('User type is required')
        return self._transaction

class BancolombiaQrBuilder(TransactionBuilder):
    def __init__(self):
        super().__init__()
        self._transaction = BancolombiaQr()

    def payment_method(self, payment_description: str, status: SandboxStatus = SandboxStatus.APPROVED) -> 'BancolombiaQrBuilder':
        data = { 'type': self._transaction.payment_method_type, 'payment_description': payment_description, 'sandbox_status': status.value }
        self._transaction.payment_method = data
        return self

    def build(self) -> BancolombiaQr:
        super().build()
        if not self._transaction.payment_method['payment_description']:
            raise ValueError('Description is required')
        return self._transaction