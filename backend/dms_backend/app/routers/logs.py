from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models import LogEntry
from ..services.logging import logging_service

router = APIRouter(
    prefix="/logs",
    tags=["logs"],
)

@router.get("/", response_model=List[dict])
async def get_logs(
    limit: int = 100,
    event_type: Optional[str] = None,
    document_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get recent log entries with optional filters"""
    logs = await logging_service.get_recent_logs(
        db=db,
        limit=limit,
        event_type=event_type,
        document_id=document_id,
        user_id=user_id
    )
    return [
        {
            "id": log.id,
            "event_type": log.event_type,
            "document_id": log.document_id,
            "user_id": log.user_id,
            "details": log.details,
            "timestamp": log.timestamp
        }
        for log in logs
    ]
