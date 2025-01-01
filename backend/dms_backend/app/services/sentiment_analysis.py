from typing import Optional, Dict, Any
from transformers import pipeline

class SentimentAnalysisService:
    """Service for analyzing document sentiment using transformers."""
    
    def __init__(self):
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            top_k=None
        )
        
    async def analyze(self, text: str) -> Optional[str]:
        """
        Analyze the sentiment of the text and return the sentiment label.
        Returns: "Positive", "Negative", or "Neutral"
        """
        if not text:
            return None
            
        try:
            # Get sentiment prediction
            result = self.sentiment_analyzer(text[:512])[0]  # Limit text length
            
            # Map sentiment scores to labels
            if result["label"] == "POSITIVE" and result["score"] > 0.6:
                return "Positive"
            elif result["label"] == "NEGATIVE" and result["score"] > 0.6:
                return "Negative"
            else:
                return "Neutral"
                
        except Exception as e:
            print(f"Error in sentiment analysis: {e}")
            return None
            
    async def get_detailed_analysis(self, text: str) -> Dict[str, Any]:
        """
        Get detailed sentiment analysis including confidence scores.
        """
        if not text:
            return {
                "sentiment": None,
                "confidence": 0.0,
                "details": {}
            }
            
        try:
            result = self.sentiment_analyzer(text[:512])[0]
            
            return {
                "sentiment": result["label"],
                "confidence": round(result["score"], 3),
                "details": {
                    "original_label": result["label"],
                    "original_score": result["score"],
                }
            }
            
        except Exception as e:
            print(f"Error in detailed sentiment analysis: {e}")
            return {
                "sentiment": None,
                "confidence": 0.0,
                "details": {"error": str(e)}
            }
            
    async def analyze_sections(self, sections: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """
        Analyze sentiment for different sections of a document.
        Input: Dictionary of section name -> text content
        Output: Dictionary of section name -> sentiment analysis
        """
        results = {}
        
        for section_name, text in sections.items():
            if not text:
                continue
                
            try:
                analysis = await self.get_detailed_analysis(text)
                results[section_name] = analysis
            except Exception as e:
                print(f"Error analyzing section {section_name}: {e}")
                results[section_name] = {
                    "sentiment": None,
                    "confidence": 0.0,
                    "details": {"error": str(e)}
                }
                
        return results
