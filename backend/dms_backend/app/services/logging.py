from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from ..models import LogEntry, Document, User

class LoggingService:
    @staticmethod
    async def log_event(
        db: Session,
        event_type: str,
        document_id: Optional[int] = None,
        user_id: Optional[int] = None,
        details: Optional[dict] = None
    ) -> LogEntry:
        """Log an event in the system."""
        log_entry = LogEntry(
            event_type=event_type,
            document_id=document_id,
            user_id=user_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    async def get_recent_logs(
        db: Session,
        limit: int = 100,
        event_type: Optional[str] = None,
        document_id: Optional[int] = None,
        user_id: Optional[int] = None
    ) -> list[LogEntry]:
        """Get recent log entries with optional filters."""
        query = db.query(LogEntry).order_by(LogEntry.timestamp.desc())
        
        if event_type:
            query = query.filter(LogEntry.event_type == event_type)
        if document_id:
            query = query.filter(LogEntry.document_id == document_id)
        if user_id:
            query = query.filter(LogEntry.user_id == user_id)
            
        return query.limit(limit).all()

logging_service = LoggingService()
