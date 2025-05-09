from .. import crud
from ..models import *
from sqlmodel import Session, select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from .deps import get_session


gameservers_router = APIRouter()


@gameservers_router.get("/")
async def get_all_gameservers(session: Session = Depends(get_session)):
    raise HTTPException(405)