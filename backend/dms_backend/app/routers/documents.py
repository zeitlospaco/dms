from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Document, Category
from ..services.workflow import setup_document_workflow
from ..services.google_drive import upload_file_to_drive
from sqlalchemy import or_
from datetime import datetime
import io

router = APIRouter()

@router.get("/search")
def search_documents(
    q: str = "",
    folder_id: Optional[int] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Search documents with optional filtering by folder and category.
    Supports text search on filename and extracted content.
    """
    query_set = db.query(Document)
    
    # Apply folder filter if specified
    if folder_id:
        query_set = query_set.filter(Document.folder_id == folder_id)
    
    # Apply category filter if specified
    if category_id:
        query_set = query_set.join(Document.categories).filter(Category.id == category_id)
    
    # Apply text search if query provided
    if q:
        # Search in both filename and extracted text
        query_set = query_set.filter(
            or_(
                Document.filename.ilike(f"%{q}%"),
                Document.extracted_text.ilike(f"%{q}%")
            )
        )
    
    # Return all matching documents
    return query_set.all()

@router.get("/{document_id}")
def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get document by ID"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    enable_workflow: bool = Form(True),
    db: Session = Depends(get_db)
):
    """
    Upload a new document to Google Drive and store its metadata.
    Supports automatic categorization and routing if workflow is enabled.
    """
    try:
        # Get admin user credentials
        admin = db.execute(
            "SELECT * FROM users WHERE role='admin' LIMIT 1"
        ).fetchone()
        
        
        if not admin or not admin.credentials: 
            raise HTTPException(
                status_code=500,
                detail="No admin credentials found for Google Drive access"
            )

        # Read file into memory
        file_contents = await file.read()
        
        # Upload to Google Drive's uncategorized folder
        drive_id = upload_file_to_drive(
            io.BytesIO(file_contents),
            file.filename,
            "14mnJGnzrlrykqnPUNFp8npJF8iOJfch_",  # Uncategorized folder ID
            admin.credentials
        )
        
        # Create document record
        document = Document(
            filename=file.filename,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            drive_id=drive_id
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Run workflow processing if enabled
        if enable_workflow:
            setup_document_workflow(document, db)
            db.commit()
        
        return {
            "id": document.id,
            "drive_id": drive_id,
            "filename": document.filename
        }
        
    except Exception as e:
        # Rollback on error
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )
