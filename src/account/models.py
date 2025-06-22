from sqlalchemy import MetaData, Table, Column, Integer, String, Double, ForeignKey

from user.models import user

account_metadata = MetaData()

account = Table(
    "account",
    account_metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey(user.c.id)),
    Column("amount", Double, nullable=False),
)