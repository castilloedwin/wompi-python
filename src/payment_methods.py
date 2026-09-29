import os
import json
import requests
from src.schemas import Transaction

class CreditCard(Transaction):
    def __init__(self):
        super().__init__()
        self.payment_method_type = 'CARD'
        self.ip = None
        self.redirect_url = None

    def create(self):
        data = super().create()
        data['redirect_url'] = self.redirect_url

        response = requests.post(f'{os.getenv('BASE_URL')}/transactions', headers={'Authorization': f'Bearer {os.getenv('PRIVATE_KEY')}'}, data=json.dumps(data))
        return response.json()