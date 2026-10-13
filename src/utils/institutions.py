import os
import requests

def get_institutions() -> dict:
    try:
        response = requests.get(f'{os.getenv('BASE_URL')}/pse/financial_institutions', headers={'Authorization': f'Bearer {os.getenv('PRIVATE_KEY')}'})
        return response.json()
    except requests.exceptions.HTTPError as error:
        return error