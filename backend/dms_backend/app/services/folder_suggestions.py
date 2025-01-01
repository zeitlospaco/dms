from typing import List, Dict
import os
from google.cloud import language_v1
from google.cloud import vision_v1
from google.oauth2 import service_account
from sqlalchemy.orm import Session
from app.models import Document, Folder
import json
import logging

class FolderSuggestionService:
    def __init__(self, db: Session):
        self.db = db
        self.credentials = service_account.Credentials.from_service_account_file(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        self.language_client = language_v1.LanguageServiceClient(credentials=self.credentials)
        self.vision_client = vision_v1.ImageAnnotatorClient(credentials=self.credentials)

    async def analyze_document_content(self, document_id: str, file_content: bytes, mime_type: str) -> Dict:
        """Analyze document content using Google Cloud APIs"""
        try:
            # Extract text based on mime type
            if mime_type.startswith('image/'):
                text = await self._extract_text_from_image(file_content)
            else:
                text = file_content.decode('utf-8')

            # Analyze text with Natural Language API
            document = language_v1.Document(
                content=text,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )

            # Analyze entities
            entities = self.language_client.analyze_entities(
                document=document
            ).entities

            # Analyze categories
            categories = self.language_client.classify_text(
                document=document
            ).categories

            return {
                'entities': [
                    {
                        'name': entity.name,
                        'type': language_v1.Entity.Type(entity.type_).name,
                        'salience': entity.salience
                    }
                    for entity in entities
                ],
                'categories': [
                    {
                        'name': category.name,
                        'confidence': category.confidence
                    }
                    for category in categories
                ]
            }
        except Exception as e:
            logging.error(f"Error analyzing document {document_id}: {str(e)}")
            return {'entities': [], 'categories': []}

    async def _extract_text_from_image(self, image_content: bytes) -> str:
        """Extract text from image using Google Cloud Vision API"""
        image = vision_v1.Image(content=image_content)
        response = self.vision_client.text_detection(image=image)
        texts = response.text_annotations

        if texts:
            return texts[0].description
        return ""

    async def get_folder_suggestions(self, document_id: str, content_analysis: Dict) -> List[Dict]:
        """Generate folder suggestions based on content analysis"""
        suggestions = []
        
        # Get existing folders for comparison
        existing_folders = self.db.query(Folder).all()
        
        # Calculate folder scores based on content similarity
        for folder in existing_folders:
            score = self._calculate_folder_similarity(folder, content_analysis)
            if score > 0.5:  # Only suggest folders with high confidence
                suggestions.append({
                    'folder_id': folder.id,
                    'folder_name': folder.name,
                    'confidence': score,
                    'reason': self._generate_suggestion_reason(folder, content_analysis)
                })

        # Sort suggestions by confidence
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:5]  # Return top 5 suggestions

    def _calculate_folder_similarity(self, folder: Folder, content_analysis: Dict) -> float:
        """Calculate similarity score between folder and document content"""
        score = 0.0
        
        # Compare folder metadata with document entities and categories
        folder_metadata = json.loads(folder.metadata) if folder.metadata else {}
        
        # Check entity matches
        for entity in content_analysis.get('entities', []):
            if entity['name'].lower() in folder_metadata.get('keywords', []):
                score += entity['salience']

        # Check category matches
        for category in content_analysis.get('categories', []):
            if category['name'] in folder_metadata.get('categories', []):
                score += category['confidence']

        return min(score, 1.0)  # Normalize score to 0-1 range

    def _generate_suggestion_reason(self, folder: Folder, content_analysis: Dict) -> str:
        """Generate human-readable reason for folder suggestion"""
        folder_metadata = json.loads(folder.metadata) if folder.metadata else {}
        
        matching_entities = [
            entity['name'] for entity in content_analysis.get('entities', [])
            if entity['name'].lower() in folder_metadata.get('keywords', [])
        ]
        
        matching_categories = [
            category['name'] for category in content_analysis.get('categories', [])
            if category['name'] in folder_metadata.get('categories', [])
        ]

        reasons = []
        if matching_entities:
            reasons.append(f"Contains similar keywords: {', '.join(matching_entities[:3])}")
        if matching_categories: 
            reasons.append(f"Matches categories: {', '.join(matching_categories[:3])}")
            
        return " and ".join(reasons) if reasons else "Based on content similarity"

    async def learn_from_user_action(self, document_id: str, selected_folder_id: str):
        """Learn from user's folder selection to improve future suggestions"""
        try:
            document = self.db.query(Document).filter(Document.id == document_id).first()
            folder = self.db.query(Folder).filter(Folder.id == selected_folder_id).first()
            
            if document and folder:
                # Update folder metadata with document insights
                folder_metadata = json.loads(folder.metadata) if folder.metadata else {}
                document_metadata = json.loads(document.metadata) if document.metadata else {}
                
                # Update keywords
                keywords = set(folder_metadata.get('keywords', []))
                if 'entities' in document_metadata:
                    for entity in document_metadata['entities']:
                        if entity['salience'] > 0.3:  # Only learn from significant entities
                            keywords.add(entity['name'].lower())
                
                # Update categories
                categories = set(folder_metadata.get('categories', []))
                if 'categories' in document_metadata:
                    for category in document_metadata['categories']:
                        if category['confidence'] > 0.5:  # Only learn from confident categories
                            categories.add(category['name'])
                
                # Save updated metadata
                folder.metadata = json.dumps({
                    **folder_metadata,
                    'keywords': list(keywords),
                    'categories': list(categories)
                })
                
                self.db.commit()
                
        except Exception as e:
            logging.error(f"Error learning from user action: {str(e)}")
