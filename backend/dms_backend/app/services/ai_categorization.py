from typing import List, Optional
from google.cloud import vision, language_v1
from google.cloud.vision_v1 import types
import io
import os
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
from datetime import datetime

class AICategorization:
    """Service for AI-based document categorization using Google Cloud APIs"""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the AI categorization service"""
        self.vision_client = vision.ImageAnnotatorClient()
        self.language_client = language_v1.LanguageServiceClient()
        self.model_path = model_path or 'models/document_classifier.joblib'
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
    
    def classify_document(self, text: str, category: Optional[str] = None) -> str:
        """Classify document text and optionally train the model"""
        # If category is provided, train the model
        if category:
            self.train_model([text], [category])
        
        # Predict category
        prediction = self.classifier.predict([text])
        return prediction[0]
    
    def train_model(self, texts: List[str], categories: List[str]) -> None:
        """Train the document classification model"""
        self.classifier.fit(texts, categories)
        
        # Save the model
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.classifier, self.model_path)
    
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
