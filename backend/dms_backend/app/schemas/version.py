from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class VersionBase(BaseModel):
    document_id: str
    user_id: str
    comment: Optional[str] = None

class VersionCreate(VersionBase):
    pass

class VersionResponse(VersionBase):
    id: int
    version_number: int
    created_at: datetime
    metadata: str

    class Config:
        orm_mode = True
