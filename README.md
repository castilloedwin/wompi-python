# Wompi Python API library

A small Python toolkit for integrating with the [Wompi](https://wompi.com) payment gateway (Colombia). It uses a **fluent builder pattern** to assemble transactions, validate them locally, sign them, and send them to the Wompi API.

## Table of contents

- [Features](#features)
- [Supported payment methods](#supported-payment-methods)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick start](#quick-start)
- [Usage by payment method](#usage-by-payment-method)
- [Builder API reference](#builder-api-reference)
- [Utilities](#utilities)
- [How it works](#how-it-works)
- [Project structure](#project-structure)
- [Running the examples](#running-the-examples)
- [Testing](#testing)

## Features

- Fluent, chainable builders for every supported payment method.
- Automatic retrieval of Wompi **acceptance tokens** (terms & conditions and personal data authorization).
- Automatic generation of the **integrity signature** (SHA-256) required by Wompi.
- Auto-generated 15-character alphanumeric transaction references.
- Client-side **card encryption** (JWE, `RSA-OAEP-256` + `A256GCM`) and tokenization.
- The tokenization public key is **cached in SQLite**, so it is fetched only once.
- PSE financial institution lookup and transaction status lookup helpers.
- Unit tests for every builder (no network access required, since HTTP calls are mocked).

## Supported payment methods

| Payment method | Builder | Wompi `type` |
|---|---|---|
| Credit / debit card | `CreditCardBuilder` | `CARD` |
| Bancolombia transfer button | `BancolombiaBuilder` | `BANCOLOMBIA_TRANSFER` |
| Bancolombia QR | `BancolombiaQrBuilder` | `BANCOLOMBIA_QR` |
| Nequi | `NequiBuilder` | `NEQUI` |
| DaviPlata | `DaviPlataBuilder` | `DAVIPLATA` |
| PSE | `PseBuilder` | `PSE` |

## Requirements

- **Python 3.12+**. The code uses f-strings that reuse the same quote type inside expressions (e.g. `f"{os.getenv('KEY')}"` written as `f'{os.getenv('KEY')}'`), which is only valid from Python 3.12 onward (PEP 701).
- A Wompi account with **sandbox** (or production) API keys. Get them from the [Wompi dashboard](https://comercios.wompi.co/).

Python dependencies (inferred from imports; the project has no `requirements.txt` yet):

| Package | Used for |
|---|---|
| `requests` | HTTP calls to the Wompi API |
| `python-dotenv` | Loading `.env` configuration |
| `jwcrypto` | JWE encryption of card data |
| `pytest` | Running the test suite |

## Installation

```bash
git clone <your-repo-url> wompi-python
cd wompi-python

python3.12 -m venv .venv
source .venv/bin/activate

pip install requests python-dotenv jwcrypto pytest
```

## Configuration

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `PUBLIC_KEY` | Your Wompi public key (e.g. `pub_test_...`). Used for acceptance tokens and card tokenization. |
| `PRIVATE_KEY` | Your Wompi private key (e.g. `prv_test_...`). Used to create and query transactions and list PSE institutions. **Keep it secret.** |
| `INTEGRITY_KEY` | Integrity secret (e.g. `test_integrity_...`). Used to sign transactions. |
| `EVENTS_KEY` | Events secret for webhook verification. Declared in `.env.example` but **not used by the code yet**. |
| `SQLITE_DATABASE` | Path to the SQLite file used to cache the tokenization public key (e.g. `wompi.db`). |
| `BASE_URL` | Wompi API base URL, **including the version**, with no trailing slash. |

Typical `BASE_URL` values:

| Environment | Value |
|---|---|
| Sandbox | `https://sandbox.wompi.co/v1` |
| Production | `https://production.wompi.co/v1` |

Example `.env` (sandbox):

```dotenv
PUBLIC_KEY=pub_test_xxxxxxxxxxxxxxxx
PRIVATE_KEY=prv_test_xxxxxxxxxxxxxxxx
EVENTS_KEY=test_events_xxxxxxxxxxxxxxxx
INTEGRITY_KEY=test_integrity_xxxxxxxxxxxxxxxx
SQLITE_DATABASE=wompi.db
BASE_URL=https://sandbox.wompi.co/v1
```

> `.env` and `*.db` are listed in `.gitignore`. Never commit your keys.

## Quick start

Every script must call `load_dotenv()` **before** creating a builder, because builders read configuration from environment variables when they are instantiated.

```python
from dotenv import load_dotenv
from src.builders.nequi import NequiBuilder

load_dotenv()

transaction = (
    NequiBuilder()
    .payment_method('3001234567')
    .acceptance_token()
    .accept_personal_auth()
    .amount_in_cents(8450000)          # COP 84,500.00
    .customer_email('juliana@example.com')
    .reference()                       # random 15-char reference
    .signature()                       # must come after amount, currency and reference
    .redirect_url('http://localhost:3000/confirmation')
    .build()                           # validates and returns the Transaction object
)

response = transaction.create()        # POST /transactions
print(response)
```

> **Amounts are in cents.** `amount_in_cents(2700000)` means COP 27,000.00.

## Usage by payment method

All snippets assume `load_dotenv()` has been called. Complete, runnable versions live in [`examples/`](examples/).

### Credit / debit card

Card data is encrypted locally with the Wompi tokenization public key, then exchanged for a card token, which the builder uses.

```python
from src.utils.encrypt import encrypt, tokenize
from src.builders.credit_card import CreditCardBuilder

card = {
    'number': '4242424242424242',   # Wompi sandbox test card
    'cvc': '123',
    'exp_month': '08',
    'exp_year': '28',
    'card_holder': 'Tomas',
}

encrypted_card = encrypt(card)
token = tokenize({'payload': encrypted_card})

transaction = (
    CreditCardBuilder()
    .payment_method(token['data']['id'], installments=1)
    .acceptance_token()
    .accept_personal_auth()
    .amount_in_cents(2700000)
    .customer_email('tomas@example.com')
    .reference()
    .signature()
    .redirect_url('http://localhost:3000/purchase')
    .build()
)
print(transaction.create())
```

### Bancolombia transfer button

```python
from src.builders.bancolombia import BancolombiaBuilder

transaction = (
    BancolombiaBuilder()
    .payment_method('Example of Bancolombia transfer button', 'http://localhost:3000/thankyou')
    .acceptance_token()
    .accept_personal_auth()
    .amount_in_cents(4300000)
    .customer_email('abc123@example.com')
    .reference()
    .signature()
    .redirect_url('http://localhost:3000/purchase')
    .build()
)
print(transaction.create())
```

`payment_method(payment_description, ecommerce_url)`. The `user_type` is fixed to `PERSON`.

### Bancolombia QR

```python
from src.builders.bancolombia import BancolombiaQrBuilder, SandboxStatus

transaction = (
    BancolombiaQrBuilder()
    .payment_method('Example of Bancolombia QR', SandboxStatus.DECLINED)
    .acceptance_token()
    .accept_personal_auth()
    .amount_in_cents(3400000)
    .customer_email('abc@example.com')
    .reference()
    .signature()
    .redirect_url('http://localhost:3000/purchase')
    .build()
)
print(transaction.create())
```

`SandboxStatus` (`APPROVED`, `DECLINED`, `ERROR`) lets you force the outcome of a sandbox transaction. It defaults to `APPROVED`.

### Nequi

```python
from src.builders.nequi import NequiBuilder

transaction = (
    NequiBuilder()
    .payment_method('3001234567')   # exactly 10 digits
    .acceptance_token()
    .accept_personal_auth()
    .amount_in_cents(8450000)
    .customer_email('juliana@example.com')
    .reference()
    .signature()
    .redirect_url('http://localhost:3000/confirmation')
    .build()
)
print(transaction.create())
```

### DaviPlata

```python
from src.builders.daviplata import DaviPlataBuilder

transaction = (
    DaviPlataBuilder()
    .payment_method('1144637222', 'Example of daviplata')   # (user_legal_id, payment_description)
    .acceptance_token()
    .accept_personal_auth()
    .amount_in_cents(5700000)
    .customer_email('jose@example.com')
    .reference()
    .signature()
    .redirect_url('http://localhost:3000/purchase')
    .build()
)
print(transaction.create())
```

The legal ID type is fixed to `CC`.

### PSE

PSE requires a financial institution code. Fetch the list first:

```python
from src.builders.pse import PseBuilder, LegalIdType, UserType
from src.utils.institutions import get_institutions

institutions = get_institutions()['data']
bank_code = institutions[0]['financial_institution_code']

transaction = (
    PseBuilder()
    .payment_method(
        user_legal_id='1144263748',
        financial_institution_code=bank_code,
        payment_description='PSE test description',
        user_legal_id_type=LegalIdType.CC,   # CC | CE | NIT
        user_type=UserType.INDIVIDUAL,       # INDIVIDUAL (0) | BUSINESS (1)
    )
    .acceptance_token()
    .accept_personal_auth()
    .amount_in_cents(12500000)
    .customer_email('xyz@example.com')
    .reference()
    .signature()
    .redirect_url('http://localhost:3000/confirmation-page')
    .build()
)
print(transaction.create())
```

### Querying a transaction

```python
from src.utils.transaction import get_transaction

print(get_transaction('<YOUR_TRANSACTION_ID>'))
```

## Builder API reference

All builders inherit from `TransactionBuilder` (`src/builders/transaction.py`) and share these chainable methods:

| Method | Description |
|---|---|
| `acceptance_token()` | Sets the merchant terms & conditions acceptance token (from `presigned_acceptance`). |
| `accept_personal_auth()` | Sets the personal data authorization token (from `presigned_personal_data_auth`). |
| `amount_in_cents(amount: int)` | Sets the amount in cents. Must be `>= 1`. |
| `currency(code: str)` | Sets the currency. Defaults to `COP`. |
| `customer_email(email: str)` | Sets the customer's email. Required. |
| `reference(reference: str = '')` | Sets a custom reference, or generates a random 15-char alphanumeric one if empty. |
| `signature()` | Computes the SHA-256 integrity signature. Generates a reference if none is set. |
| `redirect_url(url: str)` | Sets the URL the customer is redirected to after payment. |
| `payment_method(...)` | **Method-specific.** Sets the `payment_method` payload (see each section above). |
| `build()` | Validates the data and returns the transaction object. Raises `ValueError` on invalid data. |

Calling `.create()` on the built transaction sends `POST {BASE_URL}/transactions` with `Authorization: Bearer {PRIVATE_KEY}` and returns the parsed JSON response.

### Validation rules enforced by `build()`

| Builder | Rule | Error message |
|---|---|---|
| All | `amount_in_cents >= 1` | `Amount is required` |
| All | `customer_email` is set | `Email is required` |
| `CreditCardBuilder` | Token is not empty | `Token is required` |
| `BancolombiaBuilder` | `user_type` is set | `User type is required` |
| `BancolombiaQrBuilder` | `payment_description` is not empty | `Description is required` |
| `NequiBuilder` | Phone number is set | `Phone number is required` |
| `NequiBuilder` | Phone number has exactly 10 characters | `Your phone number must have ten numbers` |
| `DaviPlataBuilder` | `user_legal_id` is set | `Your personal ID is required` |
| `PseBuilder` | `user_legal_id` is set | `Legal ID is required` |
| `PseBuilder` | `user_legal_id_type` is at most 3 characters | `The type of legal ID is not valid` |
| `PseBuilder` | `user_legal_id` is longer than 6 characters | `The length of your legal ID must be greater than 6` |

### The integrity signature

`signature()` follows Wompi's integrity scheme:

```
SHA256( reference + amount_in_cents + currency + INTEGRITY_KEY )
```

Because the signature is computed from the current state of the transaction, **call `amount_in_cents()` (and `currency()`, if you change it) before `signature()`**. If you set the amount afterwards, the signature will not match and Wompi will reject the transaction.

## Utilities

| Function | Module | Description |
|---|---|---|
| `encrypt(payload: dict) -> str` | `src/utils/encrypt.py` | Encrypts a dict into a compact JWE string using the Wompi tokenization public key. |
| `tokenize(card_data: dict) -> dict` | `src/utils/encrypt.py` | `POST /tokens/cards` with the encrypted payload. Returns the token response. |
| `get_public_key() -> bytes` | `src/utils/encrypt.py` | Returns the tokenization public key, using the SQLite cache when available. |
| `get_institutions() -> dict` | `src/utils/institutions.py` | `GET /pse/financial_institutions`. |
| `get_transaction(id: str) -> dict` | `src/utils/transaction.py` | `GET /transactions/{id}`. |

## How it works

```
 ┌────────────────────┐
 │  XxxBuilder        │  fluent API, validates in build()
 │  (src/builders)    │
 └─────────┬──────────┘
           │ mutates
           ▼
 ┌────────────────────┐        ┌────────────────────────┐
 │  Transaction       │◄───────│  AcceptanceTokens      │
 │  subclass          │        │  GET /merchants/info   │
 │  (payment_methods) │        └────────────────────────┘
 └─────────┬──────────┘
           │ .create()
           ▼
   POST /transactions  ──►  Wompi API
```

1. **Instantiating a builder** creates the matching `Transaction` subclass (`src/payment_methods.py`) and calls `GET /merchants/info` (via `AcceptanceTokens`) to fetch the acceptance tokens.
2. **Chaining methods** fills in the transaction fields. `payment_method(...)` builds the payment-method-specific payload.
3. **`build()`** runs validation and returns the `Transaction`.
4. **`create()`** serializes the transaction and sends it to Wompi.

For cards, the flow adds a tokenization step:

1. `get_public_key()` reads the tokenization key from the SQLite `logs` table, or fetches it from `GET /tokens/keys/tokenization` on the first run and caches it.
2. `encrypt()` wraps the card data in a JWE (`RSA-OAEP-256` / `A256GCM`).
3. `tokenize()` exchanges the encrypted payload for a card token.
4. The token is passed to `CreditCardBuilder.payment_method()`.

## Project structure

```
wompi-python/
├── app.py                      # Entry-point stub (not functional yet)
├── .env.example                # Environment variable template
├── .gitignore
├── LICENSE                     # Apache 2.0
├── README.md
├── examples/                   # Runnable scripts, one per payment method
│   ├── bancolombia_qr.py
│   ├── bancolombia_transfer_button.py
│   ├── credit_debit_card.py
│   ├── daviplata.py
│   ├── get_transaction.py
│   ├── nequi.py
│   └── pse.py
└── src/
    ├── schemas.py              # AcceptanceTokens + base Transaction (with create())
    ├── payment_methods.py      # Transaction subclasses (CreditCard, Nequi, Pse, ...)
    ├── builders/               # One fluent builder per payment method
    │   ├── transaction.py      # Base TransactionBuilder (shared logic, signature)
    │   ├── credit_card.py
    │   ├── bancolombia.py      # BancolombiaBuilder + BancolombiaQrBuilder
    │   ├── daviplata.py
    │   ├── nequi.py
    │   └── pse.py
    ├── utils/
    │   ├── constants.py        # SQL for the public-key cache table
    │   ├── encrypt.py          # JWE encryption, tokenization, key caching
    │   ├── institutions.py     # PSE bank list
    │   └── transaction.py      # Transaction lookup
    └── tests/                  # pytest unit tests (HTTP mocked)
```

## Running the examples

Run examples from the project root as modules, so the `src` package resolves correctly:

```bash
python -m examples.nequi
python -m examples.pse
python -m examples.credit_debit_card
python -m examples.bancolombia_qr
python -m examples.bancolombia_transfer_button
python -m examples.daviplata
python -m examples.get_transaction
```

Some examples contain placeholders you must replace first (for instance `<PHONE_NUMBER>` in `nequi.py` and `<YOUR_TRANSACTION_ID>` in `get_transaction.py`). The examples hit the real Wompi API, so use **sandbox keys**.

## Testing

```bash
pytest
```

The tests live in `src/tests/` and cover each builder: field assignment, signature computation, default values, and validation errors. The `GET /merchants/info` call is patched with a fake response, so the suite runs **offline** and needs no real credentials.
