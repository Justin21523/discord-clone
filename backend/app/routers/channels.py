# backend/app/routers/channels.py
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, asc, desc

from backend.app.db.session import get_session
from backend.app.db.models import Message, User
from backend.app.schemas import MessageWithUser
from backend.app.deps import get_current_user
from backend.app.services.message_service import MessageService

router = APIRouter()

# 獲取某個頻道的歷史訊息
@router.get("/{channel_id}/messages", response_model=List[MessageWithUser])
def read_messages(
    channel_id: int,
    before: Optional[datetime] = None,  # Get messages before this timestamp
    after: Optional[datetime] = None,   # Get messages after this timestamp
    limit: int = Query(50, ge=1, le=100),  # Limit between 1 and 100
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Use the service layer to get messages
    messages = MessageService.get_messages_by_channel(
        session=session,
        channel_id=channel_id,
        before=before,
        after=after,
        limit=limit
    )
    return messages