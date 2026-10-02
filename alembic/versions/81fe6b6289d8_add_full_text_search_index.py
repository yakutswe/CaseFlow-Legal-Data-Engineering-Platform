"""add full text search index

Revision ID: 81fe6b6289d8
Revises: 84823fea808c
Create Date: 2026-10-01 08:53:10.314542

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81fe6b6289d8'
down_revision: Union[str, Sequence[str], None] = '84823fea808c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE INDEX ix_cases_opinion_fts
        ON cases
        USING GIN (
            to_tsvector(
                'english',
                opinion_text
            )
        )
        """
    )

def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS
        ix_cases_opinion_fts
        """
    )