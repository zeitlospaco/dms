from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
import json
import os

from app.database import get_db, engine
from app.models import Base, User, Document, Folder
from app.routers import auth, documents, categories, logs, notifications, optimization, feedback
from app.services.google_drive import GoogleDriveService
from app.services.folder_structure import FolderStructureService
from app.services.model_trainer import start_model_trainer

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DMS API", on_startup=[start_model_trainer])

# Configure CORS
origins = os.getenv("BACKEND_CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(categories.router)
app.include_router(logs.router)
app.include_router(notifications.router)
app.include_router(optimization.router)
app.include_router(feedback.router)

# Webhook endpoint for Google Drive Push Notifications
@app.post("/webhook/drive")
async def drive_webhook(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Handle Google Drive Push Notifications for real-time sync"""
    payload = await request.json()
    
    # Verify webhook (in production, implement proper security verification)
    if not payload.get("resource"):
        return {"status": "invalid"}
    
    # Add sync task to background tasks
    background_tasks.add_task(sync_drive_changes, payload["resource"], db)
    
    return {"status": "processing"}

async def sync_drive_changes(resource_id: str, db: Session):
    """Sync changes from Google Drive to database"""
    # Get user with valid credentials
    user = db.query(User).first()  # In production, handle multiple users
    if not user or not user.credentials:
        return
    
    # Initialize services
    creds_dict = json.loads(user.credentials)
    credentials = Credentials.from_authorized_user_info(creds_dict)
    drive_service = GoogleDriveService(credentials)
    folder_service = FolderStructureService(db, drive_service)
    
    try:
        # Get changed resource
        file_metadata = drive_service.get_file_metadata(resource_id)
        
        # Find corresponding folder/document in database
        if file_metadata["mimeType"] == "application/vnd.google-apps.folder":
            folder = db.query(Folder).filter(Folder.drive_id == resource_id).first()
            if folder:
                folder_service.sync_folder_structure(folder)
        else:
            document = db.query(Document).filter(Document.drive_id == resource_id).first()
            if document:
                # Update document metadata
                document.filename = file_metadata["name"]
                document.size_bytes = file_metadata.get("size")
                db.commit()
    
    except Exception as e:
        # Log error and handle appropriately
        print(f"Error syncing drive changes: {str(e)}")

# Health check endpoint
@app.get("/healthz")
async def healthz():
    return {"status": "healthy"}
