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
            
            # Log scopes for debugging
            print(f"Required scopes: {required_scopes}")
            print(f"Granted scopes: {granted_scopes}")
            
            # Normalize scopes by removing any version-specific parts and whitespace
            normalized_required = {scope.strip().split('auth/')[1] for scope in required_scopes}
            normalized_granted = {scope.strip().split('auth/')[1] for scope in granted_scopes}
            
            print(f"Normalized required scopes: {normalized_required}")
            print(f"Normalized granted scopes: {normalized_granted}")
            
            # Convert scopes to sets for comparison
            required_scope_set = set(GoogleDriveService.SCOPES)
            granted_scope_set = set(credentials.scopes)
            
            # Log the scope comparison for debugging
            print(f"Required scopes: {required_scope_set}")
            print(f"Granted scopes: {granted_scope_set}")
            
            # Check if required scopes are a subset of granted scopes
            # This allows Google to provide additional scopes
            if required_scope_set.issubset(granted_scope_set):
                print("All required scopes are included in granted scopes")
            else:
                print(f"Missing required scopes")
                raise ValueError("Missing required scopes")
                
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
        
        # Generate JWT token for frontend authentication
        token = credentials.token
        
        # Redirect to frontend with token
        frontend_url = os.getenv("FRONTEND_URL", "https://document-management-app-jbey7enb.devinapps.com")
        return RedirectResponse(
            url=f"{frontend_url}/dashboard?token={token}",
            status_code=302
        )
            
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
