"""empty message

Revision ID: f911e2ebb35b
Revises: 63de4c7af536
Create Date: 2024-07-25 19:00:26.457541

"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer


# revision identifiers, used by Alembic.
revision: str = 'f911e2ebb35b'
down_revision: Union[str, None] = '63de4c7af536'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    funs_table = table(
        "funs",
        column('id', Integer),
        column('answer', String),
    )
    with open("fun.json", 'r') as file:
        data = json.load(file)

    op.bulk_insert(
        funs_table,
        [{"answer": answer} for answer in data['answer']],
        multiinsert=False,
    )


def downgrade() -> None:
    pass
