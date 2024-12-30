# Document Management System (DMS)

A modern document management platform integrated with Google Drive, featuring AI-based categorization and automatic organization.

## Project Structure

```
dms/
├── backend/               # FastAPI Backend
│   └── dms_backend/
│       ├── app/          # Application code
│       ├── .env          # Backend environment configuration
│       └── pyproject.toml
├── frontend/             # React Frontend
│   └── dms_frontend/
│       ├── src/          # Source code
│       └── .env          # Frontend environment configuration
└── docs/                 # Project documentation
```

## Features

- Google Drive Integration
- AI-based Document Categorization
- Automatic Folder Organization
- Real-time Synchronization
- Modern Web Interface
- Role-based Access Control

## Technology Stack

- Backend: FastAPI (Python)
- Frontend: React with TypeScript
- Database: In-memory SQLite (Development)
- UI Components: shadcn/ui
- Authentication: OAuth 2.0 (Google)

## Development Setup

### Backend
1. Navigate to backend/dms_backend
2. Install dependencies: `poetry install`
3. Configure .env file with required credentials
4. Start development server: `poetry run fastapi dev app/main.py`

### Frontend
1. Navigate to frontend/dms_frontend
2. Install dependencies: `npm install`
3. Configure .env file with required credentials
4. Start development server: `npm run dev`

## Environment Configuration

Both frontend and backend require environment variables to be set up for:
- Google OAuth 2.0 credentials
- API endpoints
- Database configuration
- CORS settings

See the respective .env files in backend and frontend directories for required variables.
