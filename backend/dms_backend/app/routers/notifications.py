from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models import Notification
from ..services.notifications import notification_service

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)

@router.get("/", response_model=List[dict])
async def get_notifications(
    user_id: int,
    limit: int = 50,
    include_read: bool = False,
    db: Session = Depends(get_db)
):
    """Get notifications for a user"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if not include_read:
        query = query.filter(Notification.read == False)
    notifications = query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": notif.id,
            "message": notif.message,
            "event_type": notif.event_type,
            "document_id": notif.document_id,
            "created_at": notif.created_at,
            "read": notif.read,
            "read_at": notif.read_at
        }
        for notif in notifications
    ]

@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Mark a notification as read"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return await notification_service.mark_as_read(db, notification)
