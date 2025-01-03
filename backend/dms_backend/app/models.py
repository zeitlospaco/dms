from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Table, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Association table for document categories
document_categories = Table('document_categories', Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

# Model for tracking ML model performance
class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    training_size = Column(Integer)
    validation_size = Column(Integer)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # admin or user
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", back_populates="owner")
    logs = relationship("LogEntry", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    feedback = relationship("Feedback", back_populates="user")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    google_drive_id = Column(String, unique=True)
    mime_type = Column(String)
    size_bytes = Column(Float)
    extracted_text = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=True)
    ai_prediction = Column(String, nullable=True)  # Store the AI's predicted category
    prediction_timestamp = Column(DateTime, nullable=True)  # When the prediction was made
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    folder_id = Column(Integer, ForeignKey("folders.id"))
    
    owner = relationship("User", back_populates="documents")
    folder = relationship("Folder", back_populates="documents")
    categories = relationship("Category", secondary=document_categories, back_populates="documents")
    logs = relationship("LogEntry", back_populates="document")
    notifications = relationship("Notification", back_populates="document")
    feedback = relationship("Feedback", back_populates="document")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    documents = relationship("Document", secondary=document_categories, back_populates="categories")

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    document = relationship("Document", back_populates="logs")
    user = relationship("User", back_populates="logs")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="notifications")
    document = relationship("Document", back_populates="notifications")

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    correct_category = Column(String, nullable=False)
    original_category = Column(String, nullable=False)  # Store the original prediction
    confidence_score = Column(Float, nullable=True)  # AI's confidence in original prediction
    comment = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed = Column(Boolean, default=False)  # Track if feedback has been used for retraining

    document = relationship("Document", back_populates="feedback")
    user = relationship("User", back_populates="feedback")

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
