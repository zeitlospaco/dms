from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models import Folder, Document
from .google_drive import GoogleDriveService

class FolderStructureService:
    """Service for managing the folder structure in both database and Google Drive"""
    
    def __init__(self, db: Session, drive_service: GoogleDriveService):
        self.db = db
        self.drive_service = drive_service
    
    def create_year_month_structure(self, year: int, month: int, parent_folder: Folder) -> Folder:
        """Create or get year/month folder structure"""
        # First, try to find or create year folder
        year_folder = self.db.query(Folder).filter(
            Folder.parent_id == parent_folder.id,
            Folder.year == year
        ).first()
        
        if not year_folder:
            # Create in Google Drive
            drive_folder = self.drive_service.create_folder(
                f"{year}",
                parent_folder.drive_id
            )
            
            # Create in database
            year_folder = Folder(
                name=f"{year}",
                drive_id=drive_folder['id'],
                parent_id=parent_folder.id,
                year=year
            )
            self.db.add(year_folder)
            self.db.commit()
        
        # Then, try to find or create month folder
        month_folder = self.db.query(Folder).filter(
            Folder.parent_id == year_folder.id,
            Folder.month == month
        ).first()
        
        if not month_folder:
            # Create in Google Drive
            drive_folder = self.drive_service.create_folder(
                f"{month:02d}",
                year_folder.drive_id
            )
            
            # Create in database
            month_folder = Folder(
                name=f"{month:02d}",
                drive_id=drive_folder['id'],
                parent_id=year_folder.id,
                year=year,
                month=month
            )
            self.db.add(month_folder)
            self.db.commit()
        
        return month_folder
    
    def create_category_folder(self, name: str, parent_folder: Optional[Folder] = None) -> Folder:
        """Create a category folder"""
        # Create in Google Drive
        drive_folder = self.drive_service.create_folder(
            name,
            parent_folder.drive_id if parent_folder else None
        )
        
        # Create in database
        folder = Folder(
            name=name,
            drive_id=drive_folder['id'],
            parent_id=parent_folder.id if parent_folder else None
        )
        self.db.add(folder)
        self.db.commit()
        
        return folder
    
    def get_or_create_folder_path(self, path: List[str], parent_folder: Optional[Folder] = None) -> Folder:
        """Get or create a folder path"""
        current_folder = parent_folder
        
        for folder_name in path:
            next_folder = self.db.query(Folder).filter(
                Folder.parent_id == (current_folder.id if current_folder else None),
                Folder.name == folder_name
            ).first()
            
            if not next_folder:
                next_folder = self.create_category_folder(folder_name, current_folder)
            
            current_folder = next_folder
        
        return current_folder
    
    def sync_folder_structure(self, folder: Folder) -> None:
        """Sync folder structure with Google Drive"""
        # Get files from Google Drive
        drive_files = self.drive_service.list_files(folder.drive_id)
        
        # Update database with any new files
        for file in drive_files:
            if file['mimeType'] == 'application/vnd.google-apps.folder':
                # Handle subfolders
                subfolder = self.db.query(Folder).filter(
                    Folder.drive_id == file['id']
                ).first()
                
                if not subfolder:
                    subfolder = Folder(
                        name=file['name'],
                        drive_id=file['id'],
                        parent_id=folder.id
                    )
                    self.db.add(subfolder)
                    self.db.commit()
                    
                    # Recursively sync subfolder
                    self.sync_folder_structure(subfolder)
            else:
                # Handle files
                document = self.db.query(Document).filter(
                    Document.drive_id == file['id']
                ).first()
                
                if not document:
                    document = Document(
                        filename=file['name'],
                        drive_id=file['id'],
                        size_bytes=file.get('size'),
                        folder_id=folder.id
                    )
                    self.db.add(document)
        
        self.db.commit()
