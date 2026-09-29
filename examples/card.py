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

    credit_builder = credit_card.acceptance_token().accept_personal_auth().amount_in_cents(1500000).customer_email('abc@example.com').reference().signature().payment_method(token['data']['id']).redirect_url('http://localhost:3000/purchase').build()
    
    print(credit_builder.create())
    print("Token:", token)

if __name__ == "__main__":
    main()