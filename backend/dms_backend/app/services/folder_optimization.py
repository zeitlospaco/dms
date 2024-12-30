from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
from collections import defaultdict

from ..models import Folder, Document
from .folder_structure import FolderStructureService
from .google_drive import GoogleDriveService

class FolderOptimizationService:
    def __init__(self, db: Session, folder_service: FolderStructureService, drive_service: GoogleDriveService):
        self.db = db
        self.folder_service = folder_service
        self.drive_service = drive_service

    async def analyze_folder_structure(self, root_folder_id: Optional[int] = None) -> Dict:
        """Analyze folder structure and return optimization suggestions"""
        suggestions = {
            "empty_folders": [],
            "shallow_folders": [],
            "duplicate_files": [],
            "deep_paths": [],
            "naming_inconsistencies": []
        }

        # Get root folder or all top-level folders
        query = self.db.query(Folder)
        if root_folder_id:
            query = query.filter(Folder.id == root_folder_id)
        else:
            query = query.filter(Folder.parent_id == None)

        root_folders = query.all()
        
        for folder in root_folders:
            await self._analyze_folder_recursive(folder, suggestions, depth=0)
            
        return suggestions

    async def _analyze_folder_recursive(self, folder: Folder, suggestions: Dict, depth: int) -> None:
        """Recursively analyze a folder and its subfolders"""
        # Check for empty folders
        if not folder.documents and not folder.subfolders:
            suggestions["empty_folders"].append({
                "id": folder.id,
                "name": folder.name,
                "path": self._get_folder_path(folder)
            })

        # Check for shallow folders (folders with only one item)
        if len(folder.documents) + len(folder.subfolders) == 1:
            suggestions["shallow_folders"].append({
                "id": folder.id,
                "name": folder.name,
                "path": self._get_folder_path(folder)
            })

        # Check for deep paths (more than 5 levels)
        if depth > 5:
            suggestions["deep_paths"].append({
                "id": folder.id,
                "name": folder.name,
                "path": self._get_folder_path(folder),
                "depth": depth
            })

        # Check naming consistency
        await self._check_naming_consistency(folder, suggestions)

        # Recursively check subfolders
        for subfolder in folder.subfolders:
            await self._analyze_folder_recursive(subfolder, suggestions, depth + 1)

        # Check for duplicate files
        await self._find_duplicate_files(folder, suggestions)

    def _get_folder_path(self, folder: Folder) -> str:
        """Get the full path of a folder"""
        path = [folder.name]
        current = folder
        while current.parent_id:
            current = self.db.query(Folder).get(current.parent_id)
            path.insert(0, current.name)
        return " / ".join(path)

    async def _check_naming_consistency(self, folder: Folder, suggestions: Dict) -> None:
        """Check for naming inconsistencies within a folder"""
        # Example: mixing of case styles (camelCase, snake_case, etc.)
        names = [doc.filename for doc in folder.documents] + [subfolder.name for subfolder in folder.subfolders]
        
        has_camel_case = any(self._is_camel_case(name) for name in names)
        has_snake_case = any(self._is_snake_case(name) for name in names)
        
        if has_camel_case and has_snake_case:
            suggestions["naming_inconsistencies"].append({
                "folder_id": folder.id,
                "folder_name": folder.name,
                "path": self._get_folder_path(folder),
                "issue": "Mixed naming conventions (camelCase and snake_case)"
            })

    async def _find_duplicate_files(self, folder: Folder, suggestions: Dict) -> None:
        """Find duplicate files based on size and content hash"""
        # Group files by size first
        size_groups = defaultdict(list)
        for doc in folder.documents:
            if doc.size_bytes:  # Skip if size is None
                size_groups[doc.size_bytes].append(doc)

        # For files with same size, check content hash
        for size, docs in size_groups.items():
            if len(docs) > 1:
                hash_groups = defaultdict(list)
                for doc in docs:
                    content = await self.drive_service.get_file_content(doc.drive_id)
                    if content:
                        file_hash = hashlib.md5(content).hexdigest()
                        hash_groups[file_hash].append(doc)

                # Add duplicate groups to suggestions
                for file_hash, duplicate_docs in hash_groups.items():
                    if len(duplicate_docs) > 1: 
                        suggestions["duplicate_files"].append({
                            "hash": file_hash,
                            "size_bytes": size,
                            "files": [{
                                "id": doc.id,
                                "name": doc.filename,
                                "folder_path": self._get_folder_path(doc.folder)
                            } for doc in duplicate_docs]
                        })

    def _is_camel_case(self, s: str) -> bool:
        """Check if string is in camelCase"""
        return (not s[0].isupper() and 
                " " not in s and 
                "_" not in s and 
                any(c.isupper() for c in s))

    def _is_snake_case(self, s: str) -> bool:
        """Check if string is in snake_case"""
        return "_" in s and s.islower()

    async def apply_optimization(self, optimization_id: str, action: str) -> bool:
        """Apply a specific optimization suggestion"""
        # Implementation will depend on the type of optimization
        # This is a placeholder for the actual implementation
        return True

folder_optimization_service = FolderOptimizationService(None, None, None)
