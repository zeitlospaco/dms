from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, List
from app.database import get_db
from app.services.collaboration import CollaborationService

router = APIRouter(prefix="/api/collaboration", tags=["collaboration"])

# Store collaboration service instances
collaboration_services: Dict[str, CollaborationService] = {}

def get_collaboration_service(db: Session = Depends(get_db)) -> CollaborationService:
    """Get or create a collaboration service instance"""
    db_id = str(id(db))
    if db_id not in collaboration_services:
        collaboration_services[db_id] = CollaborationService(db)
    return collaboration_services[db_id]

@router.websocket("/{document_id}/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    document_id: str,
    user_id: str,
    service: CollaborationService = Depends(get_collaboration_service)
):
    """WebSocket endpoint for real-time collaboration"""
    try:
        await service.join_session(websocket, document_id, user_id)
        
        while True:
            try:
                data = await websocket.receive_json()
                
                if data['type'] == 'cursor':
                    await service.update_cursor(
                        document_id,
                        user_id,
                        data['position']
                    )
                
                elif data['type'] == 'change':
                    response = await service.make_change(
                        document_id,
                        user_id,
                        data['change']
                    )
                    await websocket.send_json(response)
                
                elif data['type'] == 'lock':
                    success = await service.lock_document(document_id, user_id)
                    await websocket.send_json({
                        'type': 'lock_response',
                        'success': success
                    })
                
                elif data['type'] == 'unlock':
                    success = await service.unlock_document(document_id, user_id)
                    await websocket.send_json({
                        'type': 'unlock_response',
                        'success': success
                    })

            except WebSocketDisconnect:
                service.leave_session(document_id, user_id)
                break
            
            except Exception as e:
                await websocket.send_json({
                    'type': 'error',
                    'message': str(e)
                })
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{document_id}/info")
async def get_session_info(
    document_id: str,
    service: CollaborationService = Depends(get_collaboration_service)
) -> Dict:
    """Get information about a collaboration session"""
    return service.get_session_info(document_id)

@router.post("/{document_id}/lock")
async def lock_document(
    document_id: str,
    user_id: str,
    service: CollaborationService = Depends(get_collaboration_service)
) -> Dict:
    """Lock a document for exclusive editing"""
    success = await service.lock_document(document_id, user_id)
    return {"success": success}

@router.post("/{document_id}/unlock")
async def unlock_document(
    document_id: str,
    user_id: str,
    service: CollaborationService = Depends(get_collaboration_service)
) -> Dict:
    """Unlock a document"""
    success = await service.unlock_document(document_id, user_id)
    return {"success": success}
