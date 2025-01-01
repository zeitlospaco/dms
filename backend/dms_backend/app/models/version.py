from sqlalchemy import Column, Integer, String, LargeBinary, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(String, index=True)
    version_number = Column(Integer)
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    comment = Column(String, nullable=True)
    file_content = Column(LargeBinary)
    metadata = Column(String)  # JSON string containing file metadata

    # Relationships
    creator = relationship("User", back_populates="document_versions")

    class Config:
        orm_mode = True
