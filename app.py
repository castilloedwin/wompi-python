from dotenv import load_dotenv
from src.builders.credit_card import CreditCardBuilder

load_dotenv()

def main():
    credit_card = CreditCardBuilder()
if __name__ == "__main__":
    main()