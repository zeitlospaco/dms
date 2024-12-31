from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Optional
from ..database import get_db
from ..services.folder_optimization import folder_optimization_service
from ..services.folder_structure import FolderStructureService
from ..services.google_drive import GoogleDriveService
from ..services.logging import logging_service

router = APIRouter(
    prefix="/optimization",
    tags=["optimization"],
)

@router.get("/analyze")
async def analyze_folder_structure(
    root_folder_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Analyze folder structure and get optimization suggestions"""
    drive_service = GoogleDriveService()
    folder_service = FolderStructureService(db, drive_service)
    
    # Initialize optimization service with dependencies
    folder_optimization_service.db = db
    folder_optimization_service.folder_service = folder_service
    folder_optimization_service.drive_service = drive_service
    
    suggestions = await folder_optimization_service.analyze_folder_structure(root_folder_id)
    
    # Log the analysis
    await logging_service.log_event(
        db=db,
        event_type="folder_analysis",
        details={"root_folder_id": root_folder_id}
    )
    
    return suggestions

@router.post("/optimize/{optimization_id}")
async def apply_optimization(
    optimization_id: str,
    action: str,
    db: Session = Depends(get_db)
):
    """Apply a specific optimization suggestion"""
    try:
        success = await folder_optimization_service.apply_optimization(optimization_id, action)
        if success:
            # Log the optimization
            await logging_service.log_event(
                db=db,
                event_type="folder_optimization",
                details={
                    "optimization_id": optimization_id,
                    "action": action
                }
            )
            return {"message": "Optimization applied successfully"}
        else:
            raise HTTPException(status_code=400, detail="Failed to apply optimization")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
