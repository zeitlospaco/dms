"""Router for search-related endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict

from ..database import get_db
from ..services.search import SearchService
from ..dependencies import get_current_user
from ..models import User

router = APIRouter(
    prefix="/search",
    tags=["search"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/")
async def search_documents(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=10, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """Search documents with semantic understanding"""
    search_service = SearchService()
    return search_service.search_documents(query, db, current_user.id, limit)

@router.get("/suggestions")
async def get_suggestions(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=5, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[str]:
    """Get search suggestions based on partial query"""
    search_service = SearchService()
    return search_service.get_suggestions(query, db, current_user.id, limit)

@router.get("/related/{document_id}")
async def get_related_documents(
    document_id: int,
    limit: int = Query(default=5, le=10),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict]:
    """Get related documents based on content similarity"""
    search_service = SearchService()
    return search_service.get_related_documents(document_id, db, limit)
