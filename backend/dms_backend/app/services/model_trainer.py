"""Background service for periodic model retraining"""
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session
from ..database import SessionLocal
from .ai_categorization import AICategorization

async def periodic_model_training():
    """Periodically retrain the model with new feedback"""
    while True:
        try:
            # Create new database session
            db = SessionLocal()
            
            # Initialize AI categorization service
            ai_service = AICategorization()
            
            # Retrain model with new feedback
            metrics = ai_service.retrain_from_feedback(db)
            
            if metrics:
                print(f"Model retrained successfully. Metrics: {metrics}")
            
        except Exception as e:
            print(f"Error during model training: {str(e)}")
        
        finally:
            db.close()
            
        # Wait for 6 hours before next training
        await asyncio.sleep(6 * 60 * 60)

async def start_model_trainer():
    """Start the periodic model training task"""
    await periodic_model_training()
