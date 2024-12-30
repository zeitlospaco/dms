from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Association table for document categories
document_categories = Table('document_categories', Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # admin or user
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", back_populates="owner")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    google_drive_id = Column(String, unique=True)
    mime_type = Column(String)
    size_bytes = Column(Float)
    extracted_text = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"))
    
    owner = relationship("User", back_populates="documents")
    folder = relationship("Folder", back_populates="documents")
    categories = relationship("Category", secondary=document_categories, back_populates="documents")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", secondary=document_categories, back_populates="categories")

class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    google_drive_id = Column(String, unique=True)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    year = Column(Integer, nullable=True)  # For year-based organization
    month = Column(Integer, nullable=True)  # For month-based organization
    created_at = Column(DateTime, default=datetime.utcnow)
    
    parent = relationship("Folder", remote_side=[id], backref="subfolders")
    documents = relationship("Document", back_populates="folder")
