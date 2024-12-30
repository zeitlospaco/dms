from typing import List, Optional, Tuple
from google.cloud import vision, language_v1
from google.cloud.vision_v1 import types
import io
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score
import joblib
import numpy as np
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import Feedback, Document, Base
from ..database import engine

class AICategorization:
    """Service for AI-based document categorization using Google Cloud APIs"""
    
    def __init__(self, model_path: Optional[str] = None, version: Optional[str] = None):
        """Initialize the AI categorization service"""
        self.vision_client = vision.ImageAnnotatorClient()
        self.language_client = language_v1.LanguageServiceClient()
        self.version = version or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.model_dir = "models"
        self.model_path = model_path or os.path.join(self.model_dir, f'document_classifier_{self.version}.joblib')
        self.metrics_path = os.path.join(self.model_dir, f'metrics_{self.version}.json')
        self.classifier = self._load_or_create_model()
    
    def _load_or_create_model(self) -> Pipeline:
        """Load existing model or create a new one"""
        try:
            return joblib.load(self.model_path)
        except:
            # Create a new model pipeline
            return Pipeline([
                ('vectorizer', TfidfVectorizer()),
                ('classifier', MultinomialNB())
            ])
    
    def extract_text(self, content: bytes) -> str:
        """Extract text from document using Google Cloud Vision API"""
        image = types.Image(content=content)
        response = self.vision_client.document_text_detection(image=image)
        
        if response.error.message:
            raise Exception(
                f'{response.error.message}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'
            )
        
        return response.full_text_annotation.text
    
    def analyze_entities(self, text: str) -> List[dict]:
        """Analyze entities in text using Google Cloud Natural Language API"""
        document = language_v1.Document(
            content=text,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        
        response = self.language_client.analyze_entities(
            request={'document': document}
        )
        
        return [{
            'name': entity.name,
            'type': language_v1.Entity.Type(entity.type_).name,
            'salience': entity.salience
        } for entity in response.entities]
    
    def classify_document(self, text: str, category: Optional[str] = None) -> Tuple[str, float]:
        """Classify document text and optionally train the model"""
        # If category is provided, train the model
        if category:
            self.train_model([text], [category], evaluate=False)
        
        
        # Predict category and get confidence score
        prediction = self.classifier.predict([text])
        confidence = np.max(self.classifier.predict_proba([text]))
        
        return prediction[0], float(confidence)
        
    def retrain_from_feedback(self, db: Session) -> dict:
        """Retrain model using feedback data"""
        # Get unprocessed feedback
        feedback_entries = db.query(Feedback).filter(
            Feedback.processed == False
        ).all()
        
        if not feedback_entries:
            return {}
        
        texts, categories = [], []
        for feedback in feedback_entries:
            document = db.query(Document).filter(
                Document.id == feedback.document_id
            ).first()
            
            if document and document.extracted_text:
                texts.append(document.extracted_text)
                categories.append(feedback.correct_category)
                
                # Mark feedback as processed
                feedback.processed = True
        
        db.commit()
        
        if not texts:
            return {}
            
        # Train model with new data and get metrics
        return self.train_model(texts, categories)
    
    def train_model(self, texts: List[str], categories: List[str], evaluate: bool = True) -> dict:
        """Train the document classification model and evaluate performance"""
        # Create directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Train the model
        self.classifier.fit(texts, categories)
        
        metrics = {}
        if evaluate and len(texts) >= 3:  # Only evaluate if we have enough samples
            # Perform cross-validation
            cv_scores = cross_val_score(self.classifier, texts, categories, cv=3)
            metrics = {
                'accuracy_mean': float(np.mean(cv_scores)),
                'accuracy_std': float(np.std(cv_scores)),
                'training_samples': len(texts),
                'timestamp': datetime.utcnow().isoformat(),
                'version': self.version
            }
            
            # Save metrics
            with open(self.metrics_path, 'w') as f:
                json.dump(metrics, f)
        
        # Save the model with version
        joblib.dump(self.classifier, self.model_path)
        
        return metrics
    
    def suggest_folder(self, text: str, entities: List[dict]) -> dict:
        """Suggest appropriate folder based on text content and entities"""
        # Get document category
        category = self.classify_document(text)
        
        # Extract date information from entities
        date_entity = next(
            (e for e in entities if e['type'] == 'DATE'),
            None
        )
        
        # Default to current date if no date found
        if date_entity:
            try:
                date = datetime.strptime(date_entity['name'], '%Y-%m-%d')
            except:
                date = datetime.now()
        else:
            date = datetime.now()
        
        return {
            'category': category,
            'year': date.year,
            'month': date.month
        }
