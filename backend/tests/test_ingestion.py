import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.mock_sources.generators import SOURCE_GENERATORS


@pytest.mark.asyncio
async def test_list_sources():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/ingest/")
    assert response.status_code == 200
    sources = response.json()
    # All three sources should be registered
    assert "crm" in sources
    assert "ticketing" in sources
    assert "hr" in sources


@pytest.mark.asyncio
async def test_ingest_crm():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/ingest/crm")

    assert response.status_code == 200
    data = response.json()

    assert data["source_name"] == "crm"
    assert data["total"] == 30       # matches limit= in get_crm_contacts
    assert data["inserted"] == 30    # all new on first run
    assert data["updated"] == 0
    assert data["duration_ms"] > 0


@pytest.mark.asyncio
async def test_ingest_is_idempotent():
    """Running ingestion twice should update, not re-insert."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post("/api/ingest/crm")          # first run
        response = await client.post("/api/ingest/crm")  # second run

    data = response.json()
    assert data["inserted"] == 0     # nothing new
    assert data["updated"] == 30     # all updated


@pytest.mark.asyncio
async def test_ingest_unknown_source_returns_404():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/api/ingest/salesforce")
    assert response.status_code == 404