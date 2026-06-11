import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.source import DataSource

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_session)]


class SourceCreate(BaseModel):
    name: str
    source_type: str
    endpoint_url: str
    config: dict = {}


class SourceResponse(BaseModel):
    id: uuid.UUID
    name: str
    source_type: str
    endpoint_url: str
    is_active: bool

    model_config = {"from_attributes": True}


@router.get("/", response_model=list[SourceResponse])
async def list_sources(session: SessionDep):
    result = await session.execute(select(DataSource))
    return result.scalars().all()


@router.post("/", response_model=SourceResponse, status_code=201)
async def create_source(data: SourceCreate, session: SessionDep):
    existing = await session.execute(
        select(DataSource).where(DataSource.name == data.name)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Source name already exists")

    source = DataSource(**data.model_dump())
    session.add(source)
    await session.commit()
    await session.refresh(source)
    return source
