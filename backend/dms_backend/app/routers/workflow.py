from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..services.workflow import WorkflowService
from ..services.notifications import NotificationService
from ..models import Document

router = APIRouter(prefix="/workflow", tags=["workflow"])

@router.post("/process/{document_id}")
async def process_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Process a document through the workflow pipeline."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    notification_service = NotificationService(db)
    workflow_service = WorkflowService(db, notification_service)
    
    await workflow_service.process_document(document)
    return {"status": "success", "message": "Document processed successfully"}

@router.get("/duplicates/{document_id}")
async def get_duplicates(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Get potential duplicate documents with similarity analysis."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    workflow_service = WorkflowService(db, NotificationService(db))
    duplicates = await workflow_service.detect_duplicates(document)
    
    return [
        {
            "document": {
                "id": dup["document"].id,
                "filename": dup["document"].filename,
                "created_at": dup["document"].created_at,
                "size": dup["document"].size,
                "topic": dup["document"].topic_label,
                "sentiment": dup["document"].sentiment_label
            },
            "similarity_score": dup["similarity_score"],
            "similarity_factors": dup["similarity_factors"]
        }
        for dup in duplicates
    ]

@router.post("/route/{document_id}")
async def route_document(
    document_id: int,
    db: Session = Depends(get_db)
):
    """Route a document to the appropriate folder."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    workflow_service = WorkflowService(db, NotificationService(db))
    target_folder = await workflow_service.route_document(document)
    
    return {
        "status": "success",
        "message": f"Document routed successfully",
        "target_folder": target_folder
    }
