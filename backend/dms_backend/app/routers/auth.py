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

from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.get("/login")
async def login(state: str):
    """Start OAuth2 login flow"""
    flow, auth_url = GoogleDriveService.create_auth_url()
    # Store state parameter in session or validate it later
    return {"auth_url": auth_url, "state": state}

@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle OAuth2 callback"""
    try:
        flow, _ = GoogleDriveService.create_auth_url()
        
        try:
            # Get credentials from flow
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Log the scopes for debugging
            print(f"Required scopes: {GoogleDriveService.SCOPES}")
            print(f"Granted scopes: {credentials.scopes}")
            
            # Convert scopes to sets for comparison
            required_scopes = {scope.strip() for scope in GoogleDriveService.SCOPES}
            granted_scopes = {scope.strip() for scope in credentials.scopes}
            
            # Check if all required scopes are included in granted scopes
            missing_scopes = required_scopes - granted_scopes
            if missing_scopes:
                print(f"Missing required scopes: {missing_scopes}")
                raise ValueError(f"Missing required scopes: {missing_scopes}")
                
        except ValueError as e:
            print(f"Scope validation error: {str(e)}")
            frontend_url = os.getenv("FRONTEND_URL", "https://document-management-app-jbey7enb.devinapps.com")
            return RedirectResponse(
                url=f"{frontend_url}/login?error=insufficient_scopes",
                status_code=302
            )
        
        # Store credentials in database (you might want to encrypt these)
        creds_dict = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }
        
        # Get user info from Google
        drive_service = GoogleDriveService(credentials)
        try:
            about = drive_service.service.about().get(fields="user").execute()
            email = about["user"]["emailAddress"]
        except Exception as e:
            print(f"Error getting user info: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to get user information from Google Drive"}
            )
        
        try:
            # Find or create user
            user = db.query(User).filter(User.email == email).first()
            if not user:
                user = User(
                    email=email,
                    credentials=json.dumps(creds_dict)
                )
                db.add(user)
            else:
                user.credentials = json.dumps(creds_dict)
            
            db.commit()
        except Exception as e:
            print(f"Database error: {str(e)}")
            db.rollback()
            return JSONResponse(
                status_code=500,
                content={"detail": "Failed to save user information"}
            )
        
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "https://document-management-app-jbey7enb.devinapps.com")
        return RedirectResponse(url=f"{frontend_url}/dashboard", status_code=302)
            
    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        frontend_url = os.getenv("FRONTEND_URL", "https://document-management-app-jbey7enb.devinapps.com")
        return RedirectResponse(
            url=f"{frontend_url}/login?error=auth_failed",
            status_code=302
        )

@router.get("/refresh")
async def refresh_token(
    db: Session = Depends(get_db)
):
    """Refresh OAuth2 token"""
    user = db.query(User).first()  # In reality, get current user
    if not user or not user.credentials:
        return JSONResponse(
            status_code=401,
            content={"detail": "Not authenticated"}
        )
    
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
            return JSONResponse(
                status_code=401,
                content={"detail": "Token refresh failed"}
            )
    
    return {"message": "Token refreshed successfully"}
