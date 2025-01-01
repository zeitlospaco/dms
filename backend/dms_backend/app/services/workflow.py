from datetime import datetime
from typing import List, Optional, Dict
import re
from sqlalchemy.orm import Session
from ..models import Document
from .notifications import NotificationService
from .document_summary import DocumentSummaryService
from .topic_modeling import TopicModelingService
from .sentiment_analysis import SentimentAnalysisService
from .ai_categorization import AICategorization

class WorkflowService:
    def __init__(self, db: Session, notification_service: NotificationService):
        self.db = db
        self.notification_service = notification_service
        self.summary_service = DocumentSummaryService()
        self.topic_service = TopicModelingService()
        self.sentiment_service = SentimentAnalysisService()
        self.ai_service = AICategorization()

    def detect_deadline(self, text: str) -> Optional[datetime]:
        """Extract potential deadline dates from document text."""
        date_patterns = [
            r'due\s+(?:by|on|before)?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'deadline[:]?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'submit\s+(?:by|before|until)\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    date_str = match.group(1)
                    return datetime.strptime(date_str, '%d/%m/%Y')
                except ValueError:
                    continue
        return None

    async def route_document(self, document: Document) -> str:
        """Route document to appropriate folder based on AI analysis."""
        if not document.content:
            return 'Uncategorized'
            
        # Get AI insights
        summary = await self.summary_service.generate_summary(document.content)
        topic = await self.topic_service.analyze(document.content)
        sentiment = await self.sentiment_service.analyze(document.content)
        keywords = await self.ai_service.extract_keywords(document.content)
        
        # Update document metadata
        document.topic_label = topic
        document.sentiment_label = sentiment
        document.keywords = keywords
        self.db.commit()
        
        # Determine folder based on content analysis
        routing_rules = {
            r'invoice|receipt|payment|bill': 'Finance',
            r'contract|agreement|legal|terms': 'Legal',
            r'report|analysis|research|study': 'Reports',
            r'meeting|minutes|agenda|discussion': 'Meetings',
            r'proposal|pitch|presentation': 'Business',
            r'manual|guide|instruction|documentation': 'Documentation'
        }

        # Check keywords first
        for keyword in keywords:
            for pattern, folder in routing_rules.items():
                if re.search(pattern, keyword.lower()):
                    return folder
                    
        # Check summary as fallback
        for pattern, folder in routing_rules.items():
            if re.search(pattern, summary.lower()):
                return folder

        # Use topic as final fallback
        if topic and topic.lower() in [f.lower() for f in routing_rules.values()]:
            return topic

        return 'Uncategorized'

    async def detect_duplicates(self, document: Document) -> List[Dict]:
        """Detect potential duplicate documents using content and metadata analysis."""
        similar_docs = []
        existing_docs = self.db.query(Document).filter(
            Document.id != document.id
        ).all()

        # Get document features if content exists
        doc_topic = None
        doc_keywords = None
        if document.content:
            doc_topic = await self.topic_service.analyze(document.content)
            doc_keywords = await self.ai_service.extract_keywords(document.content)

        for existing_doc in existing_docs:
            similarity_score = 0.0
            similarity_factors = []

            # Check size similarity
            if abs(existing_doc.size - document.size) < 100:
                similarity_score += 0.3
                similarity_factors.append("size")

            # Check filename similarity
            base_name1 = re.sub(r'\d{1,2}[-/_]\d{1,2}[-/_]\d{2,4}', '', document.filename)
            base_name2 = re.sub(r'\d{1,2}[-/_]\d{1,2}[-/_]\d{2,4}', '', existing_doc.filename)
            
            if base_name1.strip() == base_name2.strip():
                similarity_score += 0.3
                similarity_factors.append("filename")

            # Check content-based similarity if content exists
            if document.content and existing_doc.content:
                # Compare topics
                existing_topic = await self.topic_service.analyze(existing_doc.content)
                if doc_topic and existing_topic and doc_topic == existing_topic:
                    similarity_score += 0.2
                    similarity_factors.append("topic")

                # Compare keywords
                existing_keywords = await self.ai_service.extract_keywords(existing_doc.content)
                if doc_keywords and existing_keywords:
                    keyword_overlap = len(set(doc_keywords) & set(existing_keywords))
                    if keyword_overlap > 0:
                        overlap_score = min(0.2, 0.05 * keyword_overlap)
                        similarity_score += overlap_score
                        similarity_factors.append("keywords")

            if similarity_score > 0.3:  # Only include if there's significant similarity
                similar_docs.append({
                    "document": existing_doc,
                    "similarity_score": round(similarity_score, 2),
                    "similarity_factors": similarity_factors
                })

        return sorted(similar_docs, key=lambda x: x["similarity_score"], reverse=True)

    async def process_document(self, document: Document):
        """Process a document through the workflow pipeline."""
        # Create version record
        version = {
            'document_id': document.id,
            'version': document.version + 1 if document.version else 1,
            'content': document.content,
            'metadata': {
                'topic': document.topic_label,
                'sentiment': document.sentiment_label,
                'folder': document.folder
            }
        }
        document.version = version['version']
        document.versions = document.versions + [version] if document.versions else [version]

        # Process content if available
        if document.content:
            # Detect and set deadline
            deadline = self.detect_deadline(document.content)
            if deadline:
                document.deadline_date = deadline
                await self.notification_service.schedule_reminder(document.id, deadline)

            # Generate AI insights
            document.topic_label = await self.topic_service.analyze(document.content)
            document.sentiment_label = await self.sentiment_service.analyze(document.content)
            document.keywords = await self.ai_service.extract_keywords(document.content)

        # Route document
        target_folder = await self.route_document(document)
        if target_folder != document.folder:
            document.folder = target_folder
            await self.notification_service.notify_folder_change(document.id, target_folder)

        # Check for duplicates
        duplicates = await self.detect_duplicates(document)
        if duplicates:
            await self.notification_service.notify_duplicates(
                document.id, 
                [d['document'].id for d in duplicates]
            )

        # Generate smart tags
        tags = []
        if document.topic_label:
            tags.append({'label': document.topic_label, 'type': 'topic'})
        if document.sentiment_label:
            tags.append({'label': document.sentiment_label, 'type': 'sentiment'})
        if document.keywords:
            tags.extend([{'label': k, 'type': 'keyword'} for k in document.keywords[:5]])
        if document.deadline_date:
            tags.append({'label': 'Has Deadline', 'type': 'deadline'})
        document.tags = tags

        # Save changes
        self.db.commit()

        # Send update notification
        await self.notification_service.notify_document_update(
            document.id,
            {
                'version': document.version,
                'topic': document.topic_label,
                'sentiment': document.sentiment_label,
                'tags': document.tags
            }
        )
