# python -m examples.card

from dotenv import load_dotenv
from src.builders.daviplata import DaviPlataBuilder

load_dotenv()

def main():
    daviplata = DaviPlataBuilder()
    daviplata_builder = daviplata.payment_method('1144637222', 'Example of daviplata').acceptance_token().accept_personal_auth().amount_in_cents(5700000).customer_email('jose@example.com').reference().signature().redirect_url('http://localhost:3000/purchase').build()
    print(daviplata_builder.create())

if __name__ == "__main__":
    main()