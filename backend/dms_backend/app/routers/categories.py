from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os

from app.database import get_db
from app.models import Category, Document
from app.services.ai_categorization import AICategorization

router = APIRouter(prefix="/categories", tags=["categories"])

# Initialize AI service if enabled
ENABLE_AI = os.getenv("ENABLE_AI_CATEGORIZATION", "false").lower() == "true"
ai_service = AICategorization() if ENABLE_AI else None

@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    return db.query(Category).all()

@router.post("/")
def create_category(name: str, description: Optional[str] = None, db: Session = Depends(get_db)):
    """Create a new category"""
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.post("/{category_id}/train")
async def train_category(
    category_id: int,
    document_ids: List[int],
    db: Session = Depends(get_db)
):
    """Train AI model with documents for a specific category"""
    if not ENABLE_AI or not ai_service:
        raise HTTPException(status_code=400, detail="AI categorization is not enabled")
    
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    documents = db.query(Document).filter(Document.id.in_(document_ids)).all()
    if not documents:
        raise HTTPException(status_code=404, detail="No valid documents found")
    
    # Train model with documents
    for document in documents:
        if document.extracted_text:
            ai_service.classify_document(document.extracted_text, category.name)
    
    return {"message": f"Successfully trained model with {len(documents)} documents"}

@router.get("/suggest")
async def suggest_category(text: str):
    """Get category suggestion for text"""
    if not ENABLE_AI or not ai_service:
        raise HTTPException(status_code=400, detail="AI categorization is not enabled")
    
    category, confidence = ai_service.predict_category(text)
    return {
        "suggested_category": category,
        "confidence_score": confidence
    }
