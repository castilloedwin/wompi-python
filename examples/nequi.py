# python -m examples.card

from dotenv import load_dotenv
from src.builders.nequi import NequiBuilder

load_dotenv()

def main():
    nequi = NequiBuilder()
    nequi_builder = nequi.payment_method('<PHONE_NUMBER>').acceptance_token().accept_personal_auth().amount_in_cents(8450000).customer_email('juliana@example.com').reference().signature().redirect_url('http://localhost:3000/confirmation').build()
    print(nequi_builder.create())

if __name__ == "__main__":
    main()