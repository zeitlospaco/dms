from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Document, DocumentVersion
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import io
import os
import json
import difflib

class VersionControlService:
    def __init__(self, db: Session):
        self.db = db
        self.credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            scopes=['https://www.googleapis.com/auth/drive']
        )
        self.drive_service = build('drive', 'v3', credentials=self.credentials)

    async def create_version(self, document_id: str, user_id: str, comment: str = None) -> DocumentVersion:
        """Create a new version of a document"""
        # Get the current file from Google Drive
        file = self.drive_service.files().get(fileId=document_id, fields='*').execute()
        
        # Download the current content
        request = self.drive_service.files().get_media(fileId=document_id)
        content = io.BytesIO()
        downloader = MediaIoBaseDownload(content, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        # Create new version record
        version = DocumentVersion(
            document_id=document_id,
            version_number=self._get_next_version_number(document_id),
            created_by=user_id,
            created_at=datetime.utcnow(),
            comment=comment,
            file_content=content.getvalue(),
            metadata=json.dumps({
                'name': file.get('name'),
                'mimeType': file.get('mimeType'),
                'size': file.get('size'),
                'modifiedTime': file.get('modifiedTime')
            })
        )
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        return version

    def _get_next_version_number(self, document_id: str) -> int:
        """Get the next version number for a document"""
        latest_version = self.db.query(DocumentVersion)\
            .filter(DocumentVersion.document_id == document_id)\
            .order_by(DocumentVersion.version_number.desc())\
            .first()
        return (latest_version.version_number + 1) if latest_version else 1

    async def get_versions(self, document_id: str) -> List[DocumentVersion]:
        """Get all versions of a document"""
        return self.db.query(DocumentVersion)\
            .filter(DocumentVersion.document_id == document_id)\
            .order_by(DocumentVersion.version_number.desc())\
            .all()

    async def restore_version(self, document_id: str, version_number: int, user_id: str) -> DocumentVersion:
        """Restore a specific version of a document"""
        version = self.db.query(DocumentVersion)\
            .filter(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version_number == version_number
            ).first()
        
        if not version:
            raise ValueError(f"Version {version_number} not found for document {document_id}")

        # Upload the version content back to Google Drive
        file_metadata = json.loads(version.metadata)
        media = MediaIoBaseUpload(
            io.BytesIO(version.file_content),
            mimetype=file_metadata['mimeType'],
            resumable=True
        )
        
        self.drive_service.files().update(
            fileId=document_id,
            media_body=media
        ).execute()

        # Create a new version record for the restoration
        return await self.create_version(
            document_id=document_id,
            user_id=user_id,
            comment=f"Restored from version {version_number}"
        )

    async def compare_versions(self, document_id: str, version1: int, version2: int) -> dict:
        """Compare two versions of a document"""
        v1 = self.db.query(DocumentVersion)\
            .filter(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version_number == version1
            ).first()
        
        v2 = self.db.query(DocumentVersion)\
            .filter(
                DocumentVersion.document_id == document_id,
                DocumentVersion.version_number == version2
            ).first()

        if not v1 or not v2:
            raise ValueError("One or both versions not found")

        # For text-based documents, create a diff
        diff = difflib.unified_diff(
            v1.file_content.decode().splitlines(),
            v2.file_content.decode().splitlines(),
            fromfile=f'Version {version1}',
            tofile=f'Version {version2}',
            lineterm=''
        )

        return {
            'diff': list(diff),
            'metadata_changes': {
                'from': json.loads(v1.metadata),
                'to': json.loads(v2.metadata)
            }
        }
