from dotenv import load_dotenv

from src.builders.transaction import Transaction
from src.builders.credit_card import CreditCardBuilder
from src.builders.bancolombia import BancolombiaBuilder, BancolombiaQrBuilder
from src.builders.daviplata import DaviPlataBuilder
from src.builders.nequi import NequiBuilder
from src.builders.pse import PseBuilder

load_dotenv()

class TransactionFactory:
    _types = {
        'credit_card': CreditCardBuilder,
        'bancolombia': BancolombiaBuilder,
        'bancolombia_qr': BancolombiaQrBuilder,
        'daviplata': DaviPlataBuilder,
        'nequi': NequiBuilder,
        'pse': PseBuilder
    }

    @classmethod
    def create(cls, type: str) -> Transaction:
        transaction_class = cls._types.get(type)
        if transaction_class is None:
            raise ValueError(f'Unsupported file {type}')
        return transaction_class()