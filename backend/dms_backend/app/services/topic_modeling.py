from typing import Optional, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF

class TopicModelingService:
    """Service for analyzing document topics using NMF (Non-negative Matrix Factorization)."""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            max_df=0.95,
            min_df=2
        )
        self.nmf_model = NMF(
            n_components=5,
            random_state=42
        )
        self.topics = [
            "Finance",
            "Legal",
            "Reports",
            "Meetings",
            "Business"
        ]
        
    async def analyze(self, text: str) -> Optional[str]:
        """
        Analyze the text and return the most likely topic.
        For now, uses a simple keyword-based approach.
        TODO: Implement more sophisticated topic modeling.
        """
        if not text:
            return None
            
        # Simple keyword-based classification for now
        topic_keywords = {
            "Finance": ["invoice", "payment", "bill", "receipt", "cost", "expense", "budget"],
            "Legal": ["contract", "agreement", "terms", "conditions", "legal", "law", "compliance"],
            "Reports": ["report", "analysis", "study", "research", "findings", "results", "data"],
            "Meetings": ["meeting", "minutes", "agenda", "discussion", "attendees", "schedule"],
            "Business": ["proposal", "strategy", "business", "plan", "project", "client"]
        }
        
        text_lower = text.lower()
        scores = {topic: 0 for topic in topic_keywords}
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[topic] += 1
                    
        if max(scores.values()) > 0:
            return max(scores.items(), key=lambda x: x[1])[0]
            
        return "Uncategorized"
        
    async def extract_topics(self, documents: List[str]) -> List[List[str]]:
        """
        Extract topics from a collection of documents.
        Returns a list of keyword lists for each topic.
        """
        if not documents:
            return []
            
        # Create document-term matrix
        try:
            dtm = self.vectorizer.fit_transform(documents)
            topic_word = self.nmf_model.fit_transform(dtm)
            
            # Get feature names (words)
            feature_names = self.vectorizer.get_feature_names_out()
            
            # Extract top words for each topic
            n_top_words = 5
            topic_keywords = []
            
            for topic_idx, topic in enumerate(self.nmf_model.components_):
                top_words_idx = topic.argsort()[:-n_top_words-1:-1]
                top_words = [feature_names[i] for i in top_words_idx]
                topic_keywords.append(top_words)
                
            return topic_keywords
            
        except ValueError:
            # Return empty list if vectorization fails
            return []
            
    async def get_document_topics(self, text: str, threshold: float = 0.1) -> List[str]:
        """
        Get all relevant topics for a document above a certain threshold.
        """
        if not text:
            return []
            
        try:
            # Transform single document
            doc_vector = self.vectorizer.transform([text])
            topic_distribution = self.nmf_model.transform(doc_vector)[0]
            
            # Get topics above threshold
            relevant_topics = []
            for topic_idx, score in enumerate(topic_distribution):
                if score > threshold:
                    relevant_topics.append(self.topics[topic_idx])
                    
            return relevant_topics
            
        except (ValueError, AttributeError):
            # Return empty list if transformation fails
            return []
