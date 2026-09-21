from dotenv import load_dotenv
from src.builders.credit_card import CreditCardBuilder

load_dotenv()

def main():
    credit_card = CreditCardBuilder()
    credit_builder = credit_card.acceptance_token().accept_personal_auth().amount_in_cents(1500000).signature().customer_email('abc@example.com').reference().redirect_url('http://localhost:3000/purchase').build()
    print(credit_builder.create())

if __name__ == "__main__":
    main()