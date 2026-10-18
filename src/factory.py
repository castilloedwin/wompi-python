from src.builders.credit_card import CreditCardBuilder
from src.builders.bancolombia import BancolombiaBuilder, BancolombiaQrBuilder, SandboxStatus
from src.builders.daviplata import DaviPlataBuilder
from src.builders.nequi import NequiBuilder
from src.builders.pse import PseBuilder, LegalIdType, UserType

class TransactionFactory:
    _types = {
        'credit_card': CreditCardBuilder,
        'bancolombia': BancolombiaBuilder,
        'bancolombia_qr': BancolombiaQrBuilder,
        'daviplata': DaviPlataBuilder,
        'nequi': NequiBuilder,
        'pse': PseBuilder
    }