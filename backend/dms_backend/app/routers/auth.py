from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import json
import os
from typing import Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.services.google_drive import GoogleDriveService
from app.models import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/login")
async def login():
    """Start OAuth2 login flow"""
    flow, auth_url = GoogleDriveService.create_auth_url()
    return {"auth_url": auth_url}

@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: str,
    db: Session = Depends(get_db)
):
    """Handle OAuth2 callback"""
    flow, _ = GoogleDriveService.create_auth_url()
    
    # Get credentials from flow
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Create service to get user info
    service = GoogleDriveService(credentials)
    
    # Store credentials in database (you might want to encrypt these)
    creds_dict = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    
    # Create or update user with credentials
    user = db.query(User).first()
    if not user:
        user = User(
            email="admin@example.com",  # Default admin user
            credentials=json.dumps(creds_dict),
            is_admin=True
        )
        db.add(user)
    else:
        user.credentials = json.dumps(creds_dict)
        user.last_login = datetime.utcnow()
    
    db.commit()
    
    # Return credentials to frontend
    frontend_url = os.getenv("FRONTEND_URL", "https://document-management-app-jbey7enb.devinapps.com")
    token = credentials.token
    # Create a simple token parameter to avoid URL encoding issues
    return RedirectResponse(
        url=f"{frontend_url}?token={token}"
    )

@router.get("/refresh")
async def refresh_token(
    db: Session = Depends(get_db)
):
    """Refresh OAuth2 token"""
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
            raise HTTPException(status_code=401, detail="Token refresh failed")
    
    return {"message": "Token refreshed successfully"}
