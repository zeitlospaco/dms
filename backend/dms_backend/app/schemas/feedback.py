from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FeedbackBase(BaseModel):
    document_id: int
    correct_category: str
    comment: Optional[str] = None

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    user_id: int
    original_category: str
    confidence_score: Optional[float]
    timestamp: datetime
    processed: bool

    class Config:
        from_attributes = True
