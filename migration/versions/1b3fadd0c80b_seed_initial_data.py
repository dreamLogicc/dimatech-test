"""seed_initial_data

Revision ID: 1b3fadd0c80b
Revises: b9497af71930
Create Date: 2025-06-21 13:59:49.934824

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '1b3fadd0c80b'
down_revision: Union[str, Sequence[str], None] = 'b9497af71930'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    role_table = table(
        'role',
        column('id', sa.Integer),
        column('name', sa.String)
    )

    op.bulk_insert(role_table, [
        {'id': 1, 'name': 'admin'},
        {'id': 2, 'name': 'user'}
    ])

    user_table = table(
        'user',
        column('id', sa.Integer),
        column('email', sa.String),
        column('full_name', sa.String),
        column('hashed_password', sa.String),
        column('role_id', sa.Integer)
    )

    op.bulk_insert(user_table, [
        {
            'id': 1,
            'email': 'admin@example.com',
            'full_name': 'Admin User',
            'hashed_password': '$2b$12$J3/D8U0JzoSskEYYTZVYNu9EFPP51H1XdJ.lIXiJhGISlygv18f8G',
            'role_id': 1
        },
        {
            'id': 2,
            'email': 'user@example.com',
            'full_name': 'Regular User',
            'hashed_password': '$2b$12$WAM.5gN1NQ36sZzm/JCBsO4zQgGnsjJJpnx4S7vV1mTQ7IO8NclRK',
            'role_id': 2
        }
    ])

    account_table = table(
        'account',
        column('id', sa.Integer),
        column('user_id', sa.Integer),
        column('amount', sa.Double)
    )

    op.bulk_insert(account_table, [
        {'id': 1, 'user_id': 1, 'amount': 0.0},
        {'id': 2, 'user_id': 1, 'amount': 0.0},
        {'id': 3, 'user_id': 2, 'amount': 0.0}
    ])


def downgrade():
    op.execute("DELETE FROM account")
    op.execute("DELETE FROM user")
    op.execute("DELETE FROM role")
