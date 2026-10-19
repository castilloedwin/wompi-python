# python -m examples.card
from src.factory import TransactionFactory
from src.builders.pse import LegalIdType, UserType
from src.utils.institutions import get_institutions

def main():
    pse = TransactionFactory.create('pse')
    institutions = get_institutions()
    institution_list: list[dict] = institutions['data'] # We recommend you to debug this variable to know what kind of result you want to implement
    pse_builder = pse.payment_method('1144263748', institution_list[0]['financial_institution_code'], 'PSE test description', LegalIdType.CC, UserType.INDIVIDUAL).acceptance_token().accept_personal_auth().amount_in_cents(12500000).customer_email('xyz@example.com').reference().signature().redirect_url('http://localhost:3000/confirmation-page').build()
    print(pse_builder.create())

if __name__ == "__main__":
    main()