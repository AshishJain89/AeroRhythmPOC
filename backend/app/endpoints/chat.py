from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..core.database_async import get_db
from .. import schemas
from ..services import chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/query")
async def chat_query(
    user_id: int,
    query: str,
    context: str = "None",
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Process user query and return chatbot reply, actions, and explanation ID."""
    return await chat_service.process_query(user_id, query, context, db)