from sqlalchemy import MetaData, Table, Column, Integer, String, Double, ForeignKey

from account.models import account
from user.models import user

transaction_metadata = MetaData()

transaction = Table(
    "transaction",
    transaction_metadata,
    Column("transaction_id", String, primary_key=True),
    Column("user_id", Integer, ForeignKey(user.c.id)),
    Column("account_id", Integer, ForeignKey(account.c.id)),
    Column("amount", Double, nullable=False),
    Column("signature", String, nullable=False),
)