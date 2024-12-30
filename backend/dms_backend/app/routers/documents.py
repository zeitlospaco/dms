from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
import json

from app.database import get_db
from app.models import Document, User, Folder
from app.services.google_drive import GoogleDriveService
from app.services.folder_structure import FolderStructureService

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
    db: Session = Depends(get_db),
    drive_service: GoogleDriveService = Depends(get_drive_service)
):
    """Upload a document to Google Drive and store metadata in database"""
    # Read file content
    content = await file.read()
    
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
        drive_id=drive_file['id'],
        size_bytes=drive_file.get('size'),
        folder_id=folder_id
    )
    db.add(document)
    db.commit()
    
    
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
    
    # Delete from database
    db.delete(document)
    db.commit()
    
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
    document.folder_id = folder_id
    db.commit()
    
    return document
