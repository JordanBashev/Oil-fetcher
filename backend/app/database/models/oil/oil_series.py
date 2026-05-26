from __future__ import annotations

from typing import TYPE_CHECKING

from uuid import UUID, uuid4

from sqlalchemy import String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.oil.oil_price_record import OilPriceRecord

SERIES_MAX_LENGTH = 64
SERIES_DESCRIPTION_MAX_LENGTH = 256
DUOAREA_MAX_LENGTH = 32
AREA_NAME_MAX_LENGTH = 128
PRODUCT_MAX_LENGTH = 32
PRODUCT_NAME_MAX_LENGTH = 128
PROCESS_MAX_LENGTH = 32
PROCESS_NAME_MAX_LENGTH = 128
UNITS_MAX_LENGTH = 64


class OilSeries(Base):
    __tablename__ = "oil_series"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    series: Mapped[str] = mapped_column(String(SERIES_MAX_LENGTH), unique=True, nullable=False, index=True)
    series_description: Mapped[str] = mapped_column(String(SERIES_DESCRIPTION_MAX_LENGTH), nullable=False)
    duoarea: Mapped[str] = mapped_column(String(DUOAREA_MAX_LENGTH), nullable=False)
    area_name: Mapped[str] = mapped_column(String(AREA_NAME_MAX_LENGTH), nullable=False)
    product: Mapped[str] = mapped_column(String(PRODUCT_MAX_LENGTH), nullable=False)
    product_name: Mapped[str] = mapped_column(String(PRODUCT_NAME_MAX_LENGTH), nullable=False)
    process: Mapped[str] = mapped_column(String(PROCESS_MAX_LENGTH), nullable=False)
    process_name: Mapped[str] = mapped_column(String(PROCESS_NAME_MAX_LENGTH), nullable=False)
    units: Mapped[str] = mapped_column(String(UNITS_MAX_LENGTH), nullable=False)

    price_records: Mapped[list[OilPriceRecord]] = relationship(back_populates="oil_series", cascade="all, delete-orphan")
