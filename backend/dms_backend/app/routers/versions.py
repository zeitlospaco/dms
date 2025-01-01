from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.services.version_control import VersionControlService
from app.schemas.version import VersionCreate, VersionResponse
from app.models.version import DocumentVersion

router = APIRouter(prefix="/api/versions", tags=["versions"])

@router.post("/{document_id}", response_model=VersionResponse)
async def create_version(
    document_id: str,
    version_data: VersionCreate,
    db: Session = Depends(get_db)
):
    version_service = VersionControlService(db)
    try:
        version = await version_service.create_version(
            document_id=document_id,
            user_id=version_data.user_id,
            comment=version_data.comment
        )
        return version
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{document_id}", response_model=List[VersionResponse])
async def get_versions(
    document_id: str,
    db: Session = Depends(get_db)
):
    version_service = VersionControlService(db)
    try:
        versions = await version_service.get_versions(document_id)
        return versions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{document_id}/restore/{version_number}", response_model=VersionResponse)
async def restore_version(
    document_id: str,
    version_number: int,
    user_id: str,
    db: Session = Depends(get_db)
):
    version_service = VersionControlService(db)
    try:
        version = await version_service.restore_version(
            document_id=document_id,
            version_number=version_number,
            user_id=user_id
        )
        return version
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{document_id}/compare", response_model=dict)
async def compare_versions(
    document_id: str,
    version1: int,
    version2: int,
    db: Session = Depends(get_db)
):
    version_service = VersionControlService(db)
    try:
        comparison = await version_service.compare_versions(
            document_id=document_id,
            version1=version1,
            version2=version2
        )
        return comparison
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
