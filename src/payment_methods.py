from src.schemas import Transaction

class CreditCard(Transaction):
    def __init__(self):
        super().__init__()
        self.payment_method_type = 'CARD'
        self.ip = None
        self.redirect_url = None