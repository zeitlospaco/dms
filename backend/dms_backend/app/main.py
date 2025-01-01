from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.database import get_db, engine
from app.models import Base, User, Document, Folder
from app.routers import auth, documents, categories, logs, notifications, optimization, feedback, workflow, folders
from app.services.google_drive import GoogleDriveService
from app.services.folder_structure import FolderStructureService
from app.services.model_trainer import start_model_trainer

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DMS API", on_startup=[start_model_trainer])

# Configure CORS
origins = [
    "http://localhost:5173",  # Local development
    "https://document-management-app-jbey7enb.devinapps.com",  # Production frontend
    "https://document-management-app-tunnel-6e2eiw0l.devinapps.com",  # Production backend
    "https://app-frgtiqwl.fly.dev"  # Deployed backend
]
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
app.include_router(workflow.router)
app.include_router(folders.router)

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
    # Initialize credentials from environment variables
    credentials = Credentials(
        token=os.getenv("GOOGLE_ACCESS_TOKEN"),
        refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN"),
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        token_uri="https://oauth2.googleapis.com/token"
    )
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
                document.folder = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER")  # Default to root folder
                db.commit()
    
    except Exception as e:
        # Log error and handle appropriately
        print(f"Error syncing drive changes: {str(e)}")

# Health check endpoint
@app.get("/healthz")
async def healthz():
    return {"status": "healthy"}
