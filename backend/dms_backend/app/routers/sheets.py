from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
import json
import os

from app.database import get_db
from app.models import User
from app.services.google_drive import GoogleDriveService

router = APIRouter(prefix="/sheets", tags=["sheets"])

SHEET_ID = "1ujJx7bVaKPFLUoladfWMFN7K4FixdIoIQMwO93AtmVQ"

@router.get("/test")
async def test_sheet_access(db: Session = Depends(get_db)):
    """Test access to the configured Google Sheet"""
    try:
        # Get the first user's credentials (for testing)
        user = db.query(User).first()
        if not user or not user.credentials:
            raise HTTPException(status_code=401, detail="No authenticated user found")

        # Create credentials object
        creds_dict = json.loads(user.credentials)
        credentials = Credentials.from_authorized_user_info(creds_dict)

        # Initialize Google Drive service
        drive_service = GoogleDriveService(credentials)

        # Try to get sheet metadata
        file = drive_service.get_file_metadata(SHEET_ID)
        
        return {
            "success": True,
            "message": "Successfully accessed sheet",
            "metadata": file
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error accessing sheet: {error_details}")  # This will show in the logs
        return {
            "success": False,
            "message": f"Failed to access sheet: {str(e)}\nDetails: {error_details}"
        }
