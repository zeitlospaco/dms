from typing import Dict, Optional, BinaryIO
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from oauth2client.client import OAuth2Credentials
from datetime import datetime
import io

def upload_file_to_drive(
    file_obj: BinaryIO,
    filename: str,
    parent_folder_id: str,
    credentials_dict: Dict[str, str]
) -> str:
    """
    Upload a file to Google Drive using OAuth2 credentials.
    
    Args:
        file_obj: File-like object containing the file data
        filename: Name to give the file in Google Drive
        parent_folder_id: ID of the folder to upload to
        credentials_dict: Dictionary containing OAuth2 credentials
        
    Returns:
        str: The Google Drive file ID of the uploaded file
    """
    # Convert the credentials_dict to an OAuth2Credentials instance
    creds = OAuth2Credentials(
        access_token=credentials_dict['token'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret'],
        refresh_token=credentials_dict['refresh_token'],
        token_expiry=None,
        token_uri=credentials_dict.get('token_uri', 'https://oauth2.googleapis.com/token'),
        user_agent=None
    )
    
    # Build the Drive v3 service
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Prepare the file upload
    media = MediaIoBaseUpload(
        file_obj,
        mimetype='application/octet-stream',
        resumable=True
    )
    
    # Set file metadata
    file_metadata = {
        'name': filename,
        'parents': [parent_folder_id]
    }
    
    try:
        # Create the file in Google Drive
        created_file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return created_file.get('id')
    except Exception as e:
        # Log the error and re-raise
        print(f"Error uploading file to Google Drive: {str(e)}")
        raise
