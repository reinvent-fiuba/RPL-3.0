"""activities db creation

Revision ID: 8acb53cbf546
Revises: 
Create Date: 2025-02-03 22:22:56.410819

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "8acb53cbf546"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "activity_categories",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("course_id", mysql.BIGINT(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "rpl_files",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=True),
        sa.Column("file_type", sa.String(length=255), nullable=True),
        sa.Column("data", sa.LargeBinary(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "activities",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("course_id", mysql.BIGINT(), nullable=True),
        sa.Column("activity_category_id", mysql.BIGINT(), nullable=True),
        sa.Column("name", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=255), nullable=True),
        sa.Column("is_io_tested", sa.Boolean(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.Column("starting_files_id", mysql.BIGINT(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("compilation_flags", sa.String(length=500), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_category_id"],
            ["activity_categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["starting_files_id"],
            ["rpl_files.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "activity_submissions",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("activity_id", mysql.BIGINT(), nullable=True),
        sa.Column("user_id", mysql.BIGINT(), nullable=True),
        sa.Column("response_files_id", mysql.BIGINT(), nullable=True),
        sa.Column("status", sa.String(length=255), nullable=True),
        sa.Column("is_final_solution", sa.Boolean(), nullable=False),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["response_files_id"],
            ["rpl_files.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "io_tests",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("activity_id", mysql.BIGINT(), nullable=True),
        sa.Column("name", sa.String(length=500), nullable=True),
        sa.Column("test_in", sa.Text(), nullable=True),
        sa.Column("test_out", sa.Text(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "unit_tests",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("activity_id", mysql.BIGINT(), nullable=True),
        sa.Column("test_file_id", mysql.BIGINT(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["test_file_id"],
            ["rpl_files.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "results",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("activity_submission_id", mysql.BIGINT(), nullable=True),
        sa.Column("score", sa.String(length=255), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_submission_id"],
            ["activity_submissions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "test_run",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("activity_submission_id", mysql.BIGINT(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=True),
        sa.Column("exit_message", sa.String(length=255), nullable=True),
        sa.Column("stderr", sa.Text(), nullable=True),
        sa.Column("stdout", sa.Text(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_submission_id"],
            ["activity_submissions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "io_test_run",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("test_run_id", mysql.BIGINT(), nullable=True),
        sa.Column("test_name", sa.String(length=500), nullable=True),
        sa.Column("test_in", sa.Text(), nullable=True),
        sa.Column("expected_output", sa.Text(), nullable=True),
        sa.Column("run_output", sa.Text(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["test_run.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "unit_test_run",
        sa.Column("id", mysql.BIGINT(), nullable=False),
        sa.Column("test_run_id", mysql.BIGINT(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("error_messages", sa.Text(), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["test_run.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("unit_test_run")
    op.drop_table("io_test_run")
    op.drop_table("test_run")
    op.drop_table("results")
    op.drop_table("unit_tests")
    op.drop_table("io_tests")
    op.drop_table("activity_submissions")
    op.drop_table("activities")
    op.drop_table("rpl_files")
    op.drop_table("activity_categories")
    # ### end Alembic commands ###
