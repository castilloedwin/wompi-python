# python -m examples.card

from dotenv import load_dotenv
from src.utils.encrypt import encrypt, tokenize
from src.builders.credit_card import CreditCardBuilder

load_dotenv()

def main():
    credit_card = CreditCardBuilder()
    user_card = {
        'number': '4242424242424242',
        'cvc': '123',
        'exp_month': '08',
        'exp_year': '28',
        'card_holder': 'Tomas'
    }
    encrypted_card = encrypt(user_card)
    token = tokenize({'payload': encrypted_card})

    credit_builder = credit_card.payment_method(token['data']['id']).acceptance_token().accept_personal_auth().amount_in_cents(2700000).customer_email('tomas@example.com').reference().signature().redirect_url('http://localhost:3000/purchase').build()

    print(credit_builder.create())

if __name__ == "__main__":
    main()