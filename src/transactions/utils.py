import hashlib

from transactions.schemas import Payment


def verify_signature(data: Payment, secret_key: str) -> bool:
    message = f"{data.account_id}{data.amount}{data.transaction_id}{data.user_id}{secret_key}"
    expected_signature = hashlib.sha256(message.encode()).hexdigest()
    return expected_signature == data.signature