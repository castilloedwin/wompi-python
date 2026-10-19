# python -m examples.card
from src.factory import TransactionFactory

def main():
    bancolombia_transfer_button = TransactionFactory.create('bancolombia')
    bancolombia_transfer_button_builder = bancolombia_transfer_button.payment_method('Example of Bancolombia transfer button', 'http://localhost:3000/thankyou').acceptance_token().accept_personal_auth().amount_in_cents(4300000).customer_email('abc123@example.com').reference().signature().redirect_url('http://localhost:3000/purchase').build()
    print(bancolombia_transfer_button_builder.create())

if __name__ == "__main__":
    main()