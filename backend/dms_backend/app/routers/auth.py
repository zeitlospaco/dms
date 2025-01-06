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

@router.options("/login")
async def login_options():
    """Handle preflight request for login endpoint"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "https://document-management-app-jbey7enb.devinapps.com",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization, Accept",
            "Access-Control-Max-Age": "600",
        },
    )

@router.get("/login")
async def login():
    """Start OAuth2 login flow"""
    flow, auth_url = GoogleDriveService.create_auth_url()
    return JSONResponse(
        content={"auth_url": auth_url},
        headers={
            "Access-Control-Allow-Origin": "https://document-management-app-jbey7enb.devinapps.com",
            "Access-Control-Allow-Credentials": "true",
        },
    )

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
    
    # Here you would typically get the user's email from Google's userinfo endpoint
    # and create/update the user record
    # For now, we'll use a placeholder
    user = db.query(User).first()  # In reality, query by email
    if not user:
        user = User(
            email="placeholder@example.com",
            credentials=json.dumps(creds_dict)
        )
        db.add(user)
    else:
        user.credentials = json.dumps(creds_dict)
    
    db.commit()
    
    # Redirect to frontend with token
    frontend_url = os.getenv("FRONTEND_URL", "https://document-management-app-jbey7enb.devinapps.com")
    return RedirectResponse(url=f"{frontend_url}/dashboard")

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
