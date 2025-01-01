from typing import Optional, Dict, Any
from datetime import datetime

class DocumentSummaryService:
    """Service for generating and managing document summaries."""
    
    def __init__(self):
        self.cache = {}  # Simple cache for document summaries
        
    async def generate_summary(self, document_text: str, max_length: int = 200) -> str:
        """
        Generate a summary of the document text.
        For now, returns a simple truncated version of the text.
        TODO: Implement more sophisticated summarization using NLP.
        """
        if not document_text:
            return ""
        return document_text[:max_length] + "..." if len(document_text) > max_length else document_text
    
    async def get_document_metadata(self, document_id: str) -> Dict[str, Any]:
        """
        Get metadata about a document including summary, creation date, etc.
        """
        return {
            "id": document_id,
            "summary": self.cache.get(document_id, {}).get("summary", ""),
            "last_updated": datetime.utcnow().isoformat(),
            "summary_available": document_id in self.cache
        }
    
    async def cache_summary(self, document_id: str, summary: str) -> None:
        """
        Cache a document summary for faster retrieval.
        """
        self.cache[document_id] = {
            "summary": summary,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def clear_cache(self, document_id: Optional[str] = None) -> None:
        """
        Clear the summary cache for a specific document or all documents.
        """
        if document_id:
            self.cache.pop(document_id, None)
        else:
            self.cache.clear()
