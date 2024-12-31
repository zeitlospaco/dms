"""Service for intelligent document search and recommendations"""
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from ..models import Document, User, SearchHistory
from .ai_categorization import AICategorization

class SearchService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.ai_service = AICategorization()
        
    def search_documents(
        self,
        query: str,
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[Dict]:
        """Search documents using semantic similarity and user preferences"""
        # Get all documents
        documents = db.query(Document).all()
        
        if not documents:
            return []
            
        # Extract text content
        texts = [doc.extracted_text for doc in documents if doc.extracted_text]
        if not texts:
            return []
            
        # Create document vectors
        try:
            doc_vectors = self.vectorizer.fit_transform(texts)
            query_vector = self.vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, doc_vectors)[0]
            
            # Get user's search history
            user_history = db.query(SearchHistory).filter(
                SearchHistory.user_id == user_id
            ).all()
            
            # Adjust rankings based on user history
            personalization_boost = np.zeros_like(similarities)
            for hist in user_history:
                for i, doc in enumerate(documents):
                    if (doc.category == hist.clicked_category or 
                        doc.folder_path == hist.clicked_folder):
                        personalization_boost[i] += 0.1
                        
            # Combine base similarity with personalization
            final_scores = similarities + personalization_boost
            
            # Get top results
            top_indices = np.argsort(final_scores)[-limit:][::-1]
            
            # Record search query
            search_history = SearchHistory(
                user_id=user_id,
                query=query,
                timestamp=datetime.utcnow()
            )
            db.add(search_history)
            db.commit()
            
            # Return results with scores
            return [{
                'document': documents[i],
                'score': float(final_scores[i]),
                'is_personalized': bool(personalization_boost[i] > 0)
            } for i in top_indices]
            
        except Exception as e:
            print(f"Error in semantic search: {str(e)}")
            # Fallback to basic text search
            return self._basic_text_search(query, documents, limit)
    
    def get_suggestions(
        self,
        partial_query: str,
        db: Session,
        user_id: int,
        limit: int = 5
    ) -> List[str]:
        """Get search suggestions based on partial query and user history"""
        suggestions = []
        
        # Get user's recent successful searches
        recent_searches = db.query(SearchHistory).filter(
            SearchHistory.user_id == user_id,
            SearchHistory.query.isnot(None)
        ).order_by(
            SearchHistory.timestamp.desc()
        ).limit(20).all()
        
        # Add suggestions from history that match partial query
        for search in recent_searches:
            if search.query.lower().startswith(partial_query.lower()):
                suggestions.append(search.query)
                
        # Add category-based suggestions
        categories = db.query(Document.category).distinct().all()
        for category in categories:
            if category[0] and category[0].lower().startswith(partial_query.lower()):
                suggestions.append(f"category:{category[0]}")
                
        # Add date-based suggestions
        if "date:" in partial_query.lower():
            suggestions.extend([
                "date:today",
                "date:yesterday",
                "date:this_week",
                "date:this_month",
                "date:this_year"
            ])
            
        return list(set(suggestions))[:limit]
    
    def get_related_documents(
        self,
        document_id: int,
        db: Session,
        limit: int = 5
    ) -> List[Dict]:
        """Get related documents based on content similarity"""
        # Get target document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document or not document.extracted_text:
            return []
            
        # Get all other documents
        other_docs = db.query(Document).filter(
            Document.id != document_id
        ).all()
        
        if not other_docs:
            return []
            
        # Get document texts
        texts = [doc.extracted_text for doc in other_docs if doc.extracted_text]
        if not texts:
            return []
            
        try:
            # Calculate similarities
            doc_vectors = self.vectorizer.fit_transform(
                [document.extracted_text] + texts
            )
            similarities = cosine_similarity(doc_vectors[0:1], doc_vectors[1:])[0]
            
            # Get top similar documents
            top_indices = np.argsort(similarities)[-limit:][::-1]
            
            return [{
                'document': other_docs[i],
                'similarity_score': float(similarities[i])
            } for i in top_indices]
            
        except Exception as e:
            print(f"Error finding related documents: {str(e)}")
            return []
            
    def _basic_text_search(
        self,
        query: str,
        documents: List[Document],
        limit: int
    ) -> List[Dict]:
        """Fallback basic text search"""
        results = []
        for doc in documents:
            if (query.lower() in doc.name.lower() or
                (doc.extracted_text and query.lower() in doc.extracted_text.lower())):
                results.append({
                    'document': doc,
                    'score': 1.0,
                    'is_personalized': False
                })
        return results[:limit]
