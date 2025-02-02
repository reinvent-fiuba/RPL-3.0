"""utf8_migration_script

Revision ID: 9fb2569465ef
Revises: 
Create Date: 2025-02-02 04:30:29.232694

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "9fb2569465ef"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.alter_column(
        "activities",
        "description",
        existing_type=mysql.VARCHAR(length=20000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "activities",
        "points",
        existing_type=mysql.BIGINT(),
        type_=sa.Integer(),
        existing_nullable=True,
    )
    op.alter_column(
        "io_test_run",
        "test_in",
        existing_type=mysql.VARCHAR(length=5000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "io_test_run",
        "expected_output",
        existing_type=mysql.VARCHAR(length=5000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "io_test_run",
        "run_output",
        existing_type=mysql.VARCHAR(length=5000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "io_tests",
        "test_in",
        existing_type=mysql.VARCHAR(length=5000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "io_tests",
        "test_out",
        existing_type=mysql.VARCHAR(length=5000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "test_run",
        "stderr",
        existing_type=mysql.VARCHAR(length=10000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "test_run",
        "stdout",
        existing_type=mysql.VARCHAR(length=10000),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "unit_test_run",
        "error_messages",
        existing_type=mysql.VARCHAR(length=5000),
        type_=sa.Text(),
        existing_nullable=True,
    )

    # ### end Alembic commands ###


def downgrade() -> None:

    op.alter_column(
        "unit_test_run",
        "error_messages",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=5000),
        existing_nullable=True,
    )
    op.alter_column(
        "test_run",
        "stdout",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=10000),
        existing_nullable=True,
    )
    op.alter_column(
        "test_run",
        "stderr",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=10000),
        existing_nullable=True,
    )
    op.alter_column(
        "io_tests",
        "test_out",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=5000),
        existing_nullable=True,
    )
    op.alter_column(
        "io_tests",
        "test_in",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=5000),
        existing_nullable=True,
    )
    op.alter_column(
        "io_test_run",
        "run_output",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=5000),
        existing_nullable=True,
    )
    op.alter_column(
        "io_test_run",
        "expected_output",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=5000),
        existing_nullable=True,
    )
    op.alter_column(
        "io_test_run",
        "test_in",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=5000),
        existing_nullable=True,
    )
    op.alter_column(
        "activities",
        "points",
        existing_type=sa.Integer(),
        type_=mysql.BIGINT(),
        existing_nullable=True,
    )
    op.alter_column(
        "activities",
        "description",
        existing_type=sa.Text(),
        type_=mysql.VARCHAR(length=20000),
        existing_nullable=True,
    )

    # ### end Alembic commands ###
