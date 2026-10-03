# python -m examples.card

from dotenv import load_dotenv
from src.builders.bancolombia import BancolombiaQrBuilder, SandboxStatus

load_dotenv()

def main():
    bancolombia_qr = BancolombiaQrBuilder()
    bancolombia_qr_builder = bancolombia_qr.payment_method('Example of Bancolombia QR', SandboxStatus.DECLINED).acceptance_token().accept_personal_auth().amount_in_cents(3400000).customer_email('abc@example.com').reference().signature().redirect_url('http://localhost:3000/purchase').build()
    print(bancolombia_qr_builder.create())

if __name__ == "__main__":
    main()