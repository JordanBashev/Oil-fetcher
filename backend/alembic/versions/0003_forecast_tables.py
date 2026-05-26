"""forecast tables

Revision ID: 0003_forecast_tables
Revises: 0002_oil_tables
Create Date: 2026-05-22 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_forecast_tables"
down_revision: Union[str, None] = "0002_oil_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


FORECAST_STATUS_VALUES = ("pending", "processing", "completed", "failed", "canceled")


def upgrade() -> None:
    op.create_table(
        "forecast_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(*FORECAST_STATUS_VALUES, name="forecast_status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.String(length=1024), nullable=True),
        sa.Column("dataset_version_id", sa.Uuid(), nullable=False),
        sa.Column("forecast_model", sa.String(length=64), nullable=False),
        sa.Column("history_weeks", sa.Integer(), nullable=False),
        sa.Column("horizon_weeks", sa.Integer(), nullable=False),
        sa.Column("oil_series_id", sa.Uuid(), nullable=True),
        sa.Column("units", sa.String(length=64), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_versions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["oil_series_id"], ["oil_series.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_forecast_jobs_user_id", "forecast_jobs", ["user_id"], unique=False)
    op.create_index("ix_forecast_jobs_dataset_version_id", "forecast_jobs", ["dataset_version_id"], unique=False)

    op.create_table(
        "forecast_points",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("forecast_job_id", sa.Uuid(), nullable=False),
        sa.Column("period", sa.Date(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["forecast_job_id"], ["forecast_jobs.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_forecast_points_forecast_job_id", "forecast_points", ["forecast_job_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_forecast_points_forecast_job_id", table_name="forecast_points")
    op.drop_table("forecast_points")
    op.drop_index("ix_forecast_jobs_dataset_version_id", table_name="forecast_jobs")
    op.drop_index("ix_forecast_jobs_user_id", table_name="forecast_jobs")
    op.drop_table("forecast_jobs")
