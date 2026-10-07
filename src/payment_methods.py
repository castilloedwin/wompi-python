import os
import json
import requests
from src.schemas import Transaction

class CreditCard(Transaction):
    def __init__(self):
        super().__init__()
        self.payment_method_type = 'CARD'

class Bancolombia(Transaction):
    def __init__(self):
        super().__init__()
        self.payment_method_type = 'BANCOLOMBIA_TRANSFER'
        self.payment_method_user_type = 'PERSON'

class BancolombiaQr(Transaction):
    def __init__(self):
        super().__init__()
        self.payment_method_type = 'BANCOLOMBIA_QR'

class DaviPlata(Transaction):
    def __init__(self):
        super().__init__()
        self.payment_method_type = 'DAVIPLATA'
        self.payment_method_document_type = 'CC'

class Nequi(Transaction):
    def __init__(self):
        super().__init__()
        self.payment_method_type = 'NEQUI'