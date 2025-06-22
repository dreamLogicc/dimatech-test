from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey

auth_metadata = MetaData()

role = Table(
    "role",
    auth_metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
)

user = Table(
    "user",
    auth_metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String, nullable=False),
    Column("full_name", String, nullable=False),
    Column("hashed_password", String, nullable=False),
    Column("role_id", Integer, ForeignKey(role.c.id))
)