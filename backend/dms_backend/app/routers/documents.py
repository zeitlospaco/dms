from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
import json
import os

from app.database import get_db
from app.models import Document, User, Folder, Category
from app.services.google_drive import GoogleDriveService
from app.services.folder_structure import FolderStructureService
from app.services.ai_categorization import AICategorization
from app.services.logging import logging_service
from app.services.notifications import notification_service

# Initialize AI service if enabled
ENABLE_AI = os.getenv("ENABLE_AI_CATEGORIZATION", "false").lower() == "true"
ai_service = AICategorization() if ENABLE_AI else None

router = APIRouter(prefix="/documents", tags=["documents"])

def get_drive_service(db: Session = Depends(get_db)) -> GoogleDriveService:
    """Get authenticated Google Drive service"""
    user = db.query(User).first()  # In reality, get current user
    if not user or not user.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    creds_dict = json.loads(user.credentials)
    credentials = Credentials.from_authorized_user_info(creds_dict)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh()
            
            # Update stored credentials
            creds_dict = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }
            user.credentials = json.dumps(creds_dict)
            db.commit()
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return GoogleDriveService(credentials)

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    folder_id: Optional[int] = None,
    category_name: Optional[str] = None,
    db: Session = Depends(get_db),
    drive_service: GoogleDriveService = Depends(get_drive_service)
):
    """Upload a document to Google Drive and store metadata in database"""
    try:
        # Read file content
        content = await file.read()
        
        # Process with AI if enabled
        extracted_text = None
        confidence_score = None
        suggested_category = None
        suggested_folder = None
        
        if ENABLE_AI and ai_service:
            try:
                # Extract text using Google Cloud Vision
                extracted_text = ai_service.extract_text(content)
                
                # Analyze entities and get suggestions
                entities = ai_service.analyze_entities(extracted_text)
                suggestions = ai_service.suggest_folder(extracted_text, entities)
                
                # Get category suggestion
                if category_name:
                    # Use provided category for training
                    confidence_score = ai_service.classify_document(extracted_text, category_name)
                    suggested_category = category_name
                else:
                    # Get AI suggestion
                    suggested_category, confidence_score = ai_service.predict_category(extracted_text)
                
                # Update folder suggestion
                if not folder_id and suggestions:
                    folder_service = FolderStructureService(db, drive_service)
                    suggested_folder = folder_service.create_year_month_structure(
                        suggestions.get('year'),
                        suggestions.get('month'),
                        None  # Root folder
                    )
                    folder_id = suggested_folder.id
            except Exception as e:
                print(f"AI processing error: {str(e)}")
                # Continue without AI processing
        
        # Get target folder
        folder = None
        if folder_id:
            folder = db.query(Folder).filter(Folder.id == folder_id).first()
            if not folder:
                raise HTTPException(status_code=404, detail="Folder not found")
        
        # Upload to Google Drive
        drive_file = drive_service.upload_file(
            name=file.filename,
            content=content,
            mime_type=file.content_type,
            parent_id=folder.drive_id if folder else None
        )
        
        # Create document record
        document = Document(
            filename=file.filename,
            google_drive_id=drive_file['id'],
            mime_type=file.content_type,
            size_bytes=drive_file.get('size'),
            folder_id=folder_id,
            extracted_text=extracted_text,
            confidence_score=confidence_score
        )
        
        # Add category if suggested or provided
        if suggested_category or category_name:
            category = db.query(Category).filter(
                Category.name == (category_name or suggested_category)
            ).first()
            if not category:
                category = Category(name=category_name or suggested_category)
                db.add(category)
            document.categories.append(category)
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Log document upload
        await logging_service.log_event(
            db=db,
            event_type="document_upload",
            document_id=document.id,
            user_id=None,  # TODO: Get from auth
            details={"filename": document.filename, "size": document.size_bytes}
        )
        
        # Send notification
        await notification_service.create_notification(
            db=db,
            user_id=None,  # TODO: Get from auth
            message=f"New document uploaded: {document.filename}",
            event_type="document_upload",
            document_id=document.id
        )
        
        return {
            "document": document,
            "ai_processing": {
                "category_suggestion": suggested_category,
                "confidence_score": confidence_score,
                "folder_suggestion": {
                    "id": suggested_folder.id if suggested_folder else None,
                    "name": suggested_folder.name if suggested_folder else None
                } if suggested_folder else None
            } if ENABLE_AI else None
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )
    
    
    return document

@router.get("/{document_id}")
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    drive_service: GoogleDriveService = Depends(get_drive_service)
):
    """Get document metadata"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get latest metadata from Google Drive
    drive_metadata = drive_service.get_file_metadata(document.drive_id)
    
    # Update local metadata if needed
    if drive_metadata.get('size') != document.size_bytes:
        document.size_bytes = drive_metadata.get('size')
        db.commit()
    
    return document

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    drive_service: GoogleDriveService = Depends(get_drive_service)
):
    """Delete a document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Delete from Google Drive
    drive_service.delete_file(document.drive_id)
    
    # Log deletion
    await logging_service.log_event(
        db=db,
        event_type="document_delete",
        document_id=document.id,
        user_id=None,  # TODO: Get from auth
        details={"filename": document.filename}
    )
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    # Send notification
    await notification_service.create_notification(
        db=db,
        user_id=None,  # TODO: Get from auth
        message=f"Document deleted: {document.filename}",
        event_type="document_delete",
        document_id=document.id
    )
    
    return {"message": "Document deleted successfully"}

@router.post("/{document_id}/move")
async def move_document(
    document_id: int,
    folder_id: int,
    db: Session = Depends(get_db),
    drive_service: GoogleDriveService = Depends(get_drive_service)
):
    """Move a document to a different folder"""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    folder = db.query(Folder).filter(Folder.id == folder_id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Move in Google Drive
    drive_service.move_file(document.drive_id, folder.drive_id)
    
    # Update database
    old_folder_id = document.folder_id
    document.folder_id = folder_id
    db.commit()
    
    # Log move
    await logging_service.log_event(
        db=db,
        event_type="document_move",
        document_id=document.id,
        user_id=None,  # TODO: Get from auth
        details={
            "filename": document.filename,
            "from_folder_id": old_folder_id,
            "to_folder_id": folder_id
        }
    )
    
    # Send notification
    await notification_service.create_notification(
        db=db,
        user_id=None,  # TODO: Get from auth
        message=f"Document moved: {document.filename}",
        event_type="document_move",
        document_id=document.id
    )
    
    return document
