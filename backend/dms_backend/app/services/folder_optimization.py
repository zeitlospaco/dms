from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import hashlib
from collections import defaultdict
from sqlalchemy import func

from ..models import Folder, Document, Feedback, Category
from .folder_structure import FolderStructureService
from .google_drive import GoogleDriveService
from .ai_categorization import AICategorization

class FolderOptimizationService:
    def __init__(self, db: Session, folder_service: FolderStructureService, drive_service: GoogleDriveService, ai_service: AICategorization):
        self.db = db
        self.folder_service = folder_service
        self.drive_service = drive_service
        self.ai_service = ai_service

    async def analyze_folder_structure(self, root_folder_id: Optional[int] = None, include_ai_suggestions: bool = True) -> Dict:
        """Analyze folder structure and return optimization suggestions
        
        Args:
            root_folder_id: Optional ID of the root folder to analyze
            include_ai_suggestions: Whether to include AI-based suggestions for categorization
        """
        suggestions = {
            "empty_folders": [],
            "shallow_folders": [],
            "duplicate_files": [],
            "deep_paths": [],
            "naming_inconsistencies": [],
            "category_mismatches": [],
            "folder_merges": []
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
            
        # Analyze category mismatches
        self._analyze_category_mismatches(folder, suggestions)

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

    def _get_category_folder_mapping(self) -> Dict[str, List[int]]:
        """Get mapping of categories to folder IDs based on document distribution"""
        mapping = defaultdict(list)
        
        # Query documents with their categories and folders
        docs = self.db.query(Document).filter(Document.folder_id.isnot(None)).all()
        
        for doc in docs:
            if doc.categories:
                for category in doc.categories:
                    mapping[category.name].append(doc.folder_id)
        
        # Keep only folders that have a significant number of documents from a category
        refined_mapping = {}
        for category, folder_ids in mapping.items():
            # Count occurrences of each folder
            folder_counts = defaultdict(int)
            for fid in folder_ids:
                folder_counts[fid] += 1
            
            # Keep folders that contain at least 30% of documents from this category
            total_docs = len(folder_ids)
            significant_folders = [
                fid for fid, count in folder_counts.items()
                if count / total_docs >= 0.3
            ]
            
            if significant_folders:
                refined_mapping[category] = significant_folders
        
        return refined_mapping
    
    def _analyze_category_mismatches(self, folder: Folder, suggestions: Dict) -> None:
        """Analyze category mismatches based on AI predictions and feedback"""
        # Get documents with AI predictions
        docs = self.db.query(Document).filter(
            Document.folder_id == folder.id,
            Document.ai_prediction.isnot(None)
        ).all()
        
        # Get category-folder mapping
        category_folders = self._get_category_folder_mapping()
        
        for doc in docs:
            # Check if document's current folder matches its predicted category
            if doc.ai_prediction in category_folders:
                expected_folders = category_folders[doc.ai_prediction]
                if folder.id not in expected_folders:
                    # Check if prediction was corrected by feedback
                    feedback = self.db.query(Feedback).filter(
                        Feedback.document_id == doc.id
                    ).order_by(Feedback.timestamp.desc()).first()
                    
                    
                    if not feedback or feedback.correct_category == doc.ai_prediction:
                        suggestions["category_mismatches"].append({
                            "document_id": doc.id,
                            "document_name": doc.filename,
                            "current_folder": {
                                "id": folder.id,
                                "name": folder.name,
                                "path": self._get_folder_path(folder)
                            },
                            "suggested_folders": [
                                {
                                    "id": fid,
                                    "name": self.db.query(Folder).get(fid).name,
                                    "path": self._get_folder_path(self.db.query(Folder).get(fid))
                                }
                                for fid in expected_folders
                            ],
                            "predicted_category": doc.ai_prediction
                        })
    
    def _suggest_folder_merges(self, suggestions: Dict) -> None:
        """Suggest folder merges based on category distribution and feedback patterns"""
        category_folders = self._get_category_folder_mapping()
        
        # Analyze folders with similar category distributions
        for category, folder_ids in category_folders.items():
            if len(folder_ids) > 1:
                folders = [self.db.query(Folder).get(fid) for fid in folder_ids]
                
                # Check if folders have similar naming patterns
                for i in range(len(folders)):
                    for j in range(i + 1, len(folders)):
                        if self._folders_similar(folders[i], folders[j]):
                            suggestions["folder_merges"].append({
                                "category": category,
                                "folder1": {
                                    "id": folders[i].id,
                                    "name": folders[i].name,
                                    "path": self._get_folder_path(folders[i])
                                },
                                "folder2": {
                                    "id": folders[j].id,
                                    "name": folders[j].name,
                                    "path": self._get_folder_path(folders[j])
                                }
                            })
    
    def _folders_similar(self, folder1: Folder, folder2: Folder) -> bool:
        """Check if two folders are similar enough to be merged"""
        # Check if folders are in the same year/month structure
        if folder1.year == folder2.year and folder1.month == folder2.month:
            return True
            
        # Check if folders have similar names
        name1 = folder1.name.lower()
        name2 = folder2.name.lower()
        
        # Calculate similarity ratio
        longer = max(len(name1), len(name2))
        distance = sum(a != b for a, b in zip(name1, name2))
        similarity = 1 - (distance / longer)
        
        return similarity > 0.7
    
    async def apply_optimization(self, optimization_id: str, action: str, params: Dict = None) -> bool:
        """Apply a specific optimization suggestion
        
        Args:
            optimization_id: ID of the optimization suggestion
            action: Type of optimization to apply (merge_folders, move_document, delete_empty)
            params: Additional parameters needed for the optimization
        """
        try:
            if action == "merge_folders":
                source_id = params.get("source_folder_id")
                target_id = params.get("target_folder_id")
                
                source_folder = self.db.query(Folder).get(source_id)
                target_folder = self.db.query(Folder).get(target_id)
                
                if not source_folder or not target_folder:
                    return False
                
                # Move all documents to target folder
                for doc in source_folder.documents:
                    doc.folder_id = target_folder.id
                    # Update drive location
                    await self.drive_service.move_file(doc.drive_id, target_folder.drive_id)
                
                # Move all subfolders to target folder
                for subfolder in source_folder.subfolders:
                    subfolder.parent_id = target_folder.id
                    # Update drive location
                    await self.drive_service.move_file(subfolder.drive_id, target_folder.drive_id)
                
                # Delete the empty source folder
                self.db.delete(source_folder)
                await self.drive_service.delete_file(source_folder.drive_id)
                
            elif action == "move_document":
                doc_id = params.get("document_id")
                target_folder_id = params.get("target_folder_id")
                
                document = self.db.query(Document).get(doc_id)
                target_folder = self.db.query(Folder).get(target_folder_id)
                
                if not document or not target_folder:
                    return False
                
                # Update document's folder
                old_folder_id = document.folder_id
                document.folder_id = target_folder_id
                
                # Move file in Google Drive
                await self.drive_service.move_file(document.drive_id, target_folder.drive_id)
                
                # Update AI prediction if needed
                if document.ai_prediction:
                    # Record the move as feedback for the AI
                    feedback = Feedback(
                        document_id=document.id,
                        original_category=document.ai_prediction,
                        correct_category=target_folder.category.name if target_folder.category else None,
                        feedback_type="folder_move",
                        processed=False
                    )
                    self.db.add(feedback)
                
            elif action == "delete_empty":
                folder_id = params.get("folder_id")
                folder = self.db.query(Folder).get(folder_id)
                
                if not folder or folder.documents or folder.subfolders:
                    return False
                
                # Delete folder from database and drive
                self.db.delete(folder)
                await self.drive_service.delete_file(folder.drive_id)
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error applying optimization: {str(e)}")
            return False

folder_optimization_service = FolderOptimizationService(None, None, None, None)
