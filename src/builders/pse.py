from enum import Enum
from .transaction import TransactionBuilder
from src.payment_methods import Pse

class LegalIdType(Enum):
    CC = 'CC'
    CE = 'CE'
    NIT = 'NIT'

class UserType(Enum):
    INDIVIDUAL = 0 # Persona natural
    BUSINESS = 1 # Jurídica

class PseBuilder(TransactionBuilder):
    def __init__(self):
        super().__init__()
        self._transaction = Pse()

    def payment_method(self, user_legal_id: str, financial_institution_code: str, payment_description: str, user_legal_id_type: LegalIdType = LegalIdType.CC, user_type: UserType = UserType.INDIVIDUAL) -> 'PseBuilder':
        data = {
            'type': self._transaction.payment_method_type,
            'user_type': user_type.value,
            'user_legal_id_type': user_legal_id_type.value,
            'user_legal_id': user_legal_id,
            'financial_institution_code': financial_institution_code,
            'payment_description': payment_description
        }
        self._transaction.payment_method = data
        return self

    def build(self) -> Pse:
        super().build()
        if not self._transaction.payment_method['user_legal_id']:
            raise ValueError('Legal ID is required')
        if len(self._transaction.payment_method['user_legal_id_type']) > 3:
            raise ValueError('The type of legal ID is not valid')
        if not len(self._transaction.payment_method['user_legal_id']) > 6:
            raise ValueError('The length of your legal ID must be greater than 6')
        return self._transaction