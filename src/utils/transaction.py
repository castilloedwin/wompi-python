import os
import requests

def get_transaction(transaction_id: str) -> dict:
    try:
        response = requests.get(f'{os.getenv('BASE_URL')}/transactions/{transaction_id}', headers={'Authorization': f'Bearer {os.getenv('PRIVATE_KEY')}'})
        return response.json()
    except requests.exceptions.HTTPError as error:
        return error