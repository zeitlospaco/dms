from typing import List, Optional
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fastapi import HTTPException
import google.auth.transport.requests
import os
import io

class GoogleDriveService:
    """Service for interacting with Google Drive API"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self, credentials: Optional[Credentials] = None):
        """Initialize the Google Drive service with optional credentials"""
        if not credentials:
            # Load credentials from environment variables
            credentials = Credentials(
                token=os.getenv('GOOGLE_ACCESS_TOKEN'),
                refresh_token=os.getenv('GOOGLE_REFRESH_TOKEN'),
                token_uri=os.getenv('GOOGLE_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                client_id=os.getenv('GOOGLE_CLIENT_ID'),
                client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
                scopes=[
                    'https://www.googleapis.com/auth/drive.file',
                    'https://www.googleapis.com/auth/drive.metadata.readonly',
                    'https://www.googleapis.com/auth/drive'
                ]
            )
        
        self.credentials = credentials
        self.service = None
        
        # Check if token needs refresh
        if credentials.expired and credentials.refresh_token:
            request = google.auth.transport.requests.Request()
            credentials.refresh(request)
        
        self.service = build('drive', 'v3', credentials=credentials)
    
    @classmethod
    def create_auth_url(cls) -> tuple[Flow, str]:
        """Create OAuth2 authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uri": os.getenv("GOOGLE_OAUTH_REDIRECT_URI")
                }
            },
            scopes=cls.SCOPES
        )
        auth_url = flow.authorization_url(prompt='consent')[0]
        return flow, auth_url
    
    def create_folder(self, name: str, parent_id: Optional[str] = None) -> dict:
        """Create a folder in Google Drive"""
        if not self.service:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        return self.service.files().create(
            body=file_metadata,
            fields='id, name, createdTime, modifiedTime'
        ).execute()
    
    def upload_file(self, name: str, content: bytes, mime_type: str, parent_id: Optional[str] = None) -> dict:
        """Upload a file to Google Drive"""
        if not self.service:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        file_metadata = {'name': name}
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        media = MediaIoBaseUpload(
            io.BytesIO(content),
            mimetype=mime_type,
            resumable=True
        )
        
        return self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, size, createdTime, modifiedTime'
        ).execute()
    
    def get_file_metadata(self, file_id: str) -> dict:
        """Get metadata for a file"""
        if not self.service:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        return self.service.files().get(
            fileId=file_id,
            fields='id, name, size, createdTime, modifiedTime, parents'
        ).execute()
    
    def list_files(self, folder_id: Optional[str] = None, page_size: int = 100) -> List[dict]:
        """List files in a folder"""
        if not self.service:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        query = []
        if folder_id:
            query.append(f"'{folder_id}' in parents")
        query.append("mimeType != 'application/vnd.google-apps.folder'")
        
        results = self.service.files().list(
            pageSize=page_size,
            q=" and ".join(query),
            fields='files(id, name, size, createdTime, modifiedTime, mimeType)'
        ).execute()
        
        return results.get('files', [])
        
    def list_folders(self, parent_id: Optional[str] = None) -> List[dict]:
        """List folders in a parent folder"""
        if not self.service:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        query = ["mimeType = 'application/vnd.google-apps.folder'"]
        if parent_id:
            query.append(f"'{parent_id}' in parents")
            
        results = self.service.files().list(
            q=" and ".join(query),
            fields='files(id, name, createdTime, modifiedTime)'
        ).execute()
        
        return results.get('files', [])
    
    def move_file(self, file_id: str, new_parent_id: str) -> dict:
        """Move a file to a different folder"""
        if not self.service:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Get current parents
        file = self.service.files().get(
            fileId=file_id,
            fields='parents'
        ).execute()
        
        # Remove old parents and add new one
        previous_parents = ",".join(file.get('parents', []))
        file = self.service.files().update(
            fileId=file_id,
            addParents=new_parent_id,
            removeParents=previous_parents,
            fields='id, name, parents'
        ).execute()
        
        return file
    
    def delete_file(self, file_id: str) -> None:
        """Delete a file"""
        if not self.service: 
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        self.service.files().delete(fileId=file_id).execute()
