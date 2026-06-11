from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.mock_sources.generators import SOURCE_GENERATORS
from app.services.ingestion import IngestionResult, ingest_source

router = APIRouter()

class IngestResponse(BaseModel):
    source_name: str
    source_id: str
    inserted: int
    updated: int
    total: int
    duration_ms: float


@router.post("/{source_name}", response_model=IngestResponse)
async def trigger_ingestion(source_name: str) -> IngestResponse:
    """
    Ingest all records from the named source.
    Safe to call multiple times — subsequent calls update existing records.
    """
    if source_name not in SOURCE_GENERATORS:
        # FastAPI turns HTTPException into the correct HTTP response automatically
        raise HTTPException(
            status_code=404,
            detail=f"Source '{source_name}' not found. Available: {list(SOURCE_GENERATORS)}",
        )

    result: IngestionResult = await ingest_source(source_name)

    # Pydantic builds from a dataclass directly
    return IngestResponse(
        source_name=result.source_name,
        source_id=result.source_id,
        inserted=result.inserted,
        updated=result.updated,
        total=result.total,
        duration_ms=result.duration_ms,
    )


@router.get("/", response_model=list[str])
async def list_available_sources() -> list[str]:
    """List all sources available for ingestion."""
    return list(SOURCE_GENERATORS)