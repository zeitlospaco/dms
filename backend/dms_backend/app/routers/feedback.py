from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models import Feedback, Document
from ..schemas.feedback import FeedbackCreate, Feedback as FeedbackSchema
from ..dependencies import get_current_user
from ..models import User

router = APIRouter(
    prefix="/feedback",
    tags=["feedback"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=FeedbackSchema)
async def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for document categorization"""
    # Get the document to verify it exists and get its current category
    document = db.query(Document).filter(Document.id == feedback.document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Create new feedback entry
    db_feedback = Feedback(
        document_id=feedback.document_id,
        user_id=current_user.id,
        correct_category=feedback.correct_category,
        original_category=document.ai_prediction or "",
        confidence_score=document.confidence_score,
        comment=feedback.comment,
        timestamp=datetime.utcnow(),
        processed=False
    )

    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)

    return db_feedback

@router.get("/", response_model=List[FeedbackSchema])
async def get_feedback(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get feedback entries, admin users can see all feedback"""
    if current_user.role == "admin":
        feedback = db.query(Feedback).offset(skip).limit(limit).all()
    else:
        feedback = db.query(Feedback).filter(
            Feedback.user_id == current_user.id
        ).offset(skip).limit(limit).all()
    return feedback
