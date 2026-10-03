# python -m examples.card

from dotenv import load_dotenv
from src.utils.transaction import get_transaction

load_dotenv()

def main():
    transaction = get_transaction('<YOUR_TRANSACTION_ID>')
    print(transaction)

if __name__ == "__main__":
    main()