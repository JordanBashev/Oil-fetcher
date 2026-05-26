"""oil price tables

Revision ID: 0002_oil_tables
Revises: 0001_initial
Create Date: 2026-05-21 00:00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_oil_tables"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "oil_series",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("series", sa.String(length=64), nullable=False),
        sa.Column("series_description", sa.String(length=256), nullable=False),
        sa.Column("duoarea", sa.String(length=32), nullable=False),
        sa.Column("area_name", sa.String(length=128), nullable=False),
        sa.Column("product", sa.String(length=32), nullable=False),
        sa.Column("product_name", sa.String(length=128), nullable=False),
        sa.Column("process", sa.String(length=32), nullable=False),
        sa.Column("process_name", sa.String(length=128), nullable=False),
        sa.Column("units", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("series", name="uq_oil_series_series"),
    )
    op.create_index("ix_oil_series_series", "oil_series", ["series"], unique=False)

    op.create_table(
        "dataset_versions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("hash", sa.String(length=64), nullable=False),
        sa.Column("record_count", sa.Integer(), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=32), nullable=False),
        sa.UniqueConstraint("hash", name="uq_dataset_versions_hash"),
    )
    op.create_index("ix_dataset_versions_hash", "dataset_versions", ["hash"], unique=False)

    op.create_table(
        "oil_price_records",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("oil_series_id", sa.Uuid(), nullable=False),
        sa.Column("dataset_version_id", sa.Uuid(), nullable=False),
        sa.Column("period", sa.Date(), nullable=False),
        sa.Column("value", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["oil_series_id"], ["oil_series.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["dataset_version_id"], ["dataset_versions.id"], ondelete="CASCADE"),
        sa.UniqueConstraint(
            "oil_series_id",
            "period",
            "dataset_version_id",
            name="uq_oil_price_record_series_period_version",
        ),
    )
    op.create_index("ix_oil_price_records_oil_series_id", "oil_price_records", ["oil_series_id"], unique=False)
    op.create_index("ix_oil_price_records_dataset_version_id", "oil_price_records", ["dataset_version_id"], unique=False)
    op.create_index("ix_oil_price_records_period", "oil_price_records", ["period"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_oil_price_records_period", table_name="oil_price_records")
    op.drop_index("ix_oil_price_records_dataset_version_id", table_name="oil_price_records")
    op.drop_index("ix_oil_price_records_oil_series_id", table_name="oil_price_records")
    op.drop_table("oil_price_records")
    op.drop_index("ix_dataset_versions_hash", table_name="dataset_versions")
    op.drop_table("dataset_versions")
    op.drop_index("ix_oil_series_series", table_name="oil_series")
    op.drop_table("oil_series")
