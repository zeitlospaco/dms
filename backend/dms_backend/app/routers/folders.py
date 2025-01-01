from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
import os

from app.database import get_db
from app.services.google_drive import GoogleDriveService
from app.services.folder_structure import FolderStructureService
from google.oauth2.credentials import Credentials

router = APIRouter(prefix="/api/folders", tags=["folders"])

@router.get("/list")
async def list_folders(db: Session = Depends(get_db)):
    """List all folders from Google Drive"""
    try:
        # Debug: Print environment variables
        print("Environment variables:")
        print(f"GOOGLE_ACCESS_TOKEN: {os.getenv('GOOGLE_ACCESS_TOKEN')}")
        print(f"GOOGLE_REFRESH_TOKEN: {os.getenv('GOOGLE_REFRESH_TOKEN')}")
        print(f"GOOGLE_TOKEN_URI: {os.getenv('GOOGLE_TOKEN_URI')}")
        print(f"GOOGLE_CLIENT_ID: {os.getenv('GOOGLE_CLIENT_ID')}")
        print(f"GOOGLE_CLIENT_SECRET: {os.getenv('GOOGLE_CLIENT_SECRET')}")
        
        # Initialize credentials from environment variables
        credentials = Credentials(
            token=os.getenv('GOOGLE_ACCESS_TOKEN'),
            refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
            token_uri=os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        drive_service = GoogleDriveService(credentials)
        folder_service = FolderStructureService(db, drive_service)
        
        # Get root folder ID from environment
        root_folder_id = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER", "1LkKHLBC1yg8bNhO1lI4i404jNZtKR89V")
        uncategorized_folder_id = os.getenv("GOOGLE_DRIVE_UNCATEGORIZED_FOLDER_ID", "14mnJGnzrlrykqnPUNFp8npJF8iOJfch_")
            
        # Get folder structure
        folders = drive_service.list_folders(root_folder_id)
        uncategorized_folders = drive_service.list_folders(uncategorized_folder_id)
            
        return {
            "folders": folders,
            "uncategorized": uncategorized_folders,
            "root_folder_id": root_folder_id,
            "uncategorized_folder_id": uncategorized_folder_id
        }
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "Failed to list folders",
            "context": "list_folders endpoint"
        }
        raise HTTPException(status_code=500, detail=str(error_details))

@router.get("/sync")
async def sync_folders(db: Session = Depends(get_db)):
    """Sync folder structure with Google Drive"""
    try:
        # Initialize credentials from environment variables
        credentials = Credentials(
            token=os.getenv('GOOGLE_ACCESS_TOKEN'),
            refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
            token_uri=os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
            client_id=os.getenv('GOOGLE_CLIENT_ID'),
            client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
            scopes=['https://www.googleapis.com/auth/drive.file']
        )
        drive_service = GoogleDriveService(credentials)
        folder_service = FolderStructureService(db, drive_service)
        
        # Sync folder structure
        folder_service.sync_all_folders()
        return {"status": "success", "message": "Folder structure synchronized"}
        
    except Exception as e:
        import traceback
        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "message": "Failed to sync folders",
            "context": "sync_folders endpoint"
        }
        raise HTTPException(status_code=500, detail=str(error_details))
