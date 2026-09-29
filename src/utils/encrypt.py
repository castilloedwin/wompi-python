import os
import json
import sqlite3
import requests
from jwcrypto import jwk, jwe
from src.utils.constants import CREATE_LOGS_TABLE

def get_public_key() -> bytes:
    connection = sqlite3.connect(os.getenv('SQLITE_DATABASE'))
    try:
        cursor = connection.cursor()
        cursor.execute(CREATE_LOGS_TABLE)
        cursor.execute('SELECT public_key FROM logs')
        row = cursor.fetchone()

        if row is None:
            response = requests.get(f'{os.getenv('BASE_URL')}/tokens/keys/tokenization', headers={'Authorization': f'Bearer {os.getenv('PUBLIC_KEY')}'})
            response.raise_for_status()
            payload = response.json()
    
            public_key = payload['data']['publicKey']
            print(public_key)
            if not public_key:
                raise RuntimeError('Unable to get public key')

            # Caching public_key
            cursor.execute('INSERT INTO logs (public_key) VALUES (?)', (public_key,))
            connection.commit()
            return public_key.encode('utf-8')

        # Using public_key from cache (sqlite)
        public_key = row[0]
        return public_key.encode('utf-8')
    except sqlite3.Error as error:
        print(error)
        connection.rollback()
    finally:
        connection.close()

def encrypt(payload: dict) -> str:
    key = get_public_key()
    pem_key = key.encode('utf-8') if isinstance(key, str) else key
    public_jwk = jwk.JWK.from_pem(pem_key)
    protected_header = { 'alg': 'RSA-OAEP-256', 'enc': 'A256GCM' }

    jwe_token = jwe.JWE(json.dumps(payload).encode('utf-8'), protected=protected_header)
    jwe_token.add_recipient(public_jwk)
    return jwe_token.serialize(compact=True)

def tokenize(card_data: dict) -> dict:
    response = requests.post(f'{os.getenv('BASE_URL')}/tokens/cards', data=json.dumps(card_data), headers={'Authorization': f'Bearer {os.getenv('PUBLIC_KEY')}'})
    response.raise_for_status()
    return response.json()