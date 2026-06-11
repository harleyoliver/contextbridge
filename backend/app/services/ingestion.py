"""
Ingestion service: pulls data from a source and upserts into the database.

Key Python patterns:
  - async context managers  (async with)
  - SQLAlchemy select/scalar
  - PostgreSQL dialect upsert  (insert().on_conflict_do_update)
  - dataclasses for return types
"""
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert  # postgres-specific upsert

from app.db.session import AsyncSessionLocal
from app.mock_sources.generators import SOURCE_GENERATORS
from app.models.source import DataSource, Record


# A dataclass is a way to define a return-value shape.
# Acts like a TypeScript interface that also creates an object instance.
@dataclass
class IngestionResult:
    source_name: str
    source_id: str
    inserted: int
    updated: int
    total: int
    duration_ms: float


async def ingest_source(source_name: str) -> IngestionResult:
    """
    Fetch all records from a source and upsert them into the database.
    Called by the API route — safe to call multiple times (idempotent).
    """
    generator = SOURCE_GENERATORS.get(source_name)
    if generator is None:
        # Python raises exceptions - JS throws them
        raise ValueError(f"Unknown source '{source_name}'. Valid: {list(SOURCE_GENERATORS)}")

    started_at = datetime.now(timezone.utc)

    # Pull the raw records from the mock source
    raw_records = generator()

    # 'async with' is Python's version of a using() block or try/finally pattern.
    # AsyncSessionLocal() is a context manager, it opens the session and closes
    # it automatically when the block exits, even on error.
    async with AsyncSessionLocal() as session:
        source = await _get_or_create_source(session, source_name)

        inserted = 0
        updated = 0

        for raw in raw_records:
            external_id = str(raw["id"])

            # PostgreSQL-specific upsert via SQLAlchemy's dialect layer.
            # The 'on_conflict_do_update' is INSERT ... ON CONFLICT ... DO UPDATE
            # which is atomic — no race conditions like check-then-insert.
            stmt = (
                pg_insert(Record)
                .values(
                    source_id=source.id,
                    external_id=external_id,
                    record_type=source_name,
                    raw_data=raw,
                )
                .on_conflict_do_update(
                    constraint="uq_record_source_external",
                    set_={
                        "raw_data": raw,
                        "updated_at": func.now(),
                    },
                )
                # 'returning' lets us know if it was an insert or update.
                # inserted rows have xmax = 0; updated rows have xmax > 0.
                .returning(Record.id)
            )

            result = await session.execute(stmt)
            row_id = result.scalar_one()

            # Check whether this was a fresh insert or an update.
            # Done by looking up the row's xmax system column.
            was_updated = await _was_updated(session, row_id)
            if was_updated:
                updated += 1
            else:
                inserted += 1

        await session.commit()

    duration_ms = (
        datetime.now(timezone.utc) - started_at
    ).total_seconds() * 1000

    return IngestionResult(
        source_name=source_name,
        source_id=str(source.id),
        inserted=inserted,
        updated=updated,
        total=len(raw_records),
        duration_ms=round(duration_ms, 2),
    )


async def _get_or_create_source(session, name: str) -> DataSource:
    """
    Return the DataSource row for this name, creating it if it doesn't exist.
    This is the Python pattern for 'get or create' in JS.
    """
    # select() builds a SELECT statement. scalar_one_or_none() returns the
    # first result or None — Similar to .findOne() in JS.
    result = await session.execute(
        select(DataSource).where(DataSource.name == name)
    )
    source = result.scalar_one_or_none()

    if source is None:
        source = DataSource(
            name=name,
            source_type=name,
            endpoint_url=f"mock://{name}/api/records",
        )
        session.add(source)
        # flush writes to the DB within the transaction so source.id is populated,
        # but doesn't commit, the outer commit() function does that.
        await session.flush()

    return source


async def _was_updated(session, record_id) -> bool:
    """
    PostgreSQL's xmax system column is 0 for freshly inserted rows.
    Non-zero means the row was previously written and just updated.
    """
    from sqlalchemy import text
    result = await session.execute(
        text("SELECT xmax::text::int > 0 FROM records WHERE id = :id"),
        {"id": record_id},
    )
    return result.scalar_one()