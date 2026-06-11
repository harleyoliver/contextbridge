import uuid

from sqlalchemy import JSON, String, Text, UniqueConstraint   # add UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class DataSource(Base, TimestampMixin):
    __tablename__ = "data_sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    source_type: Mapped[str] = mapped_column(String(50))
    endpoint_url: Mapped[str] = mapped_column(String(500))
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(default=True)


class Record(Base, TimestampMixin):
    __tablename__ = "records"

    # Tells SQLAlchemy about a multi-column unique constraint
    __table_args__ = (
        UniqueConstraint("source_id", "external_id", name="uq_record_source_external"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_id: Mapped[uuid.UUID] = mapped_column()
    external_id: Mapped[str] = mapped_column(String(255))
    record_type: Mapped[str] = mapped_column(String(100))
    raw_data: Mapped[dict] = mapped_column(JSON)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)