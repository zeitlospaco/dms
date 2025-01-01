from typing import List, Dict
import os
from google.cloud import language_v1
from sqlalchemy.orm import Session
from app.models import Document
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

class SemanticSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.language_client = language_v1.LanguageServiceClient.from_service_account_json(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        )

    async def process_query(self, query: str) -> Dict:
        """Process natural language query to extract key entities and sentiment"""
        try:
            document = language_v1.Document(
                content=query,
                type_=language_v1.Document.Type.PLAIN_TEXT
            )

            # Analyze entities in the query
            entity_response = self.language_client.analyze_entities(document=document)
            
            # Analyze sentiment
            sentiment_response = self.language_client.analyze_sentiment(document=document)

            # Analyze syntax for better understanding
            syntax_response = self.language_client.analyze_syntax(document=document)

            return {
                'entities': [
                    {
                        'name': entity.name,
                        'type': language_v1.Entity.Type(entity.type_).name,
                        'salience': entity.salience
                    }
                    for entity in entity_response.entities
                ],
                'sentiment': {
                    'score': sentiment_response.document_sentiment.score,
                    'magnitude': sentiment_response.document_sentiment.magnitude
                },
                'tokens': [
                    {
                        'text': token.text.content,
                        'part_of_speech': language_v1.PartOfSpeech.Tag(token.part_of_speech.tag).name
                    }
                    for token in syntax_response.tokens
                ]
            }

        except Exception as e:
            logging.error(f"Error processing query: {str(e)}")
            return {'entities': [], 'sentiment': None, 'tokens': []}

    async def search(self, query: str, limit: int = 10) -> List[Dict]:
        """Perform semantic search across documents"""
        try:
            # Process the search query
            query_analysis = await self.process_query(query)
            
            # Get all documents
            documents = self.db.query(Document).all()
            results = []

            for doc in documents:
                try:
                    # Calculate relevance score
                    score = await self._calculate_relevance(doc, query_analysis)
                    
                    if score > 0.3:  # Only include relevant results
                        results.append({
                            'document': doc,
                            'score': score,
                            'highlights': await self._generate_highlights(doc, query_analysis)
                        })
                except Exception as e:
                    logging.error(f"Error processing document {doc.id}: {str(e)}")
                    continue

            # Sort by relevance score
            results.sort(key=lambda x: x['score'], reverse=True)
            return results[:limit]

        except Exception as e:
            logging.error(f"Error in semantic search: {str(e)}")
            return []

    async def _calculate_relevance(self, document: Document, query_analysis: Dict) -> float:
        """Calculate semantic relevance between document and query"""
        try:
            doc_metadata = json.loads(document.metadata) if document.metadata else {}
            
            # Initialize score components
            entity_score = 0.0
            content_score = 0.0
            context_score = 0.0
            
            # Entity matching
            doc_entities = doc_metadata.get('entities', [])
            query_entities = query_analysis['entities']
            
            for q_entity in query_entities:
                for d_entity in doc_entities:
                    if q_entity['name'].lower() in d_entity['name'].lower() or \
                       d_entity['name'].lower() in q_entity['name'].lower():
                        entity_score += q_entity['salience'] * d_entity.get('salience', 0.5)

            # Content relevance using embeddings if available
            if 'embedding' in doc_metadata and 'query_embedding' in query_analysis:
                doc_embedding = np.array(doc_metadata['embedding'])
                query_embedding = np.array(query_analysis['query_embedding'])
                content_score = cosine_similarity(
                    doc_embedding.reshape(1, -1),
                    query_embedding.reshape(1, -1)
                )[0][0]

            # Context matching
            doc_categories = doc_metadata.get('categories', [])
            query_tokens = [token['text'].lower() for token in query_analysis['tokens']]
            
            for category in doc_categories:
                if any(token in category.lower() for token in query_tokens):
                    context_score += 0.3

            # Combine scores with weights
            final_score = (
                0.4 * entity_score +
                0.4 * content_score +
                0.2 * context_score
            )


            return min(max(final_score, 0.0), 1.0)  # Normalize to 0-1

        except Exception as e:
            logging.error(f"Error calculating relevance: {str(e)}")
            return 0.0

    async def _generate_highlights(self, document: Document, query_analysis: Dict) -> List[Dict]:
        """Generate relevant text highlights from the document"""
        try:
            highlights = []
            doc_metadata = json.loads(document.metadata) if document.metadata else {}
            
            # Extract query entities and important terms
            query_terms = set()
            for entity in query_analysis['entities']:
                query_terms.add(entity['name'].lower())
            
            for token in query_analysis['tokens']:
                if token['part_of_speech'] in ['NOUN', 'VERB', 'ADJECTIVE']:
                    query_terms.add(token['text'].lower())

            # Find matching content sections
            content_sections = doc_metadata.get('content_sections', [])
            for section in content_sections:
                section_text = section.get('text', '').lower()
                
                for term in query_terms:
                    if term in section_text:
                        # Get surrounding context
                        start_idx = max(0, section_text.find(term) - 50)
                        end_idx = min(len(section_text), section_text.find(term) + len(term) + 50)
                        
                        highlights.append({
                            'text': section.get('text')[start_idx:end_idx],
                            'term': term,
                            'relevance': section.get('relevance', 0.5)
                        })

            # Sort highlights by relevance
            highlights.sort(key=lambda x: x['relevance'], reverse=True)
            return highlights[:3]  # Return top 3 highlights

        except Exception as e:
            logging.error(f"Error generating highlights: {str(e)}")
            return []

    async def get_similar_documents(self, document_id: str, limit: int = 5) -> List[Dict]:
        """Find semantically similar documents"""
        try:
            source_doc = self.db.query(Document).filter(Document.id == document_id).first()
            if not source_doc:
                return []

            source_metadata = json.loads(source_doc.metadata) if source_doc.metadata else {}
            similar_docs = []

            # Get all other documents
            other_docs = self.db.query(Document)\
                .filter(Document.id != document_id)\
                .all()

            for doc in other_docs:
                try:
                    similarity_score = await self._calculate_document_similarity(
                        source_metadata,
                        json.loads(doc.metadata) if doc.metadata else {}
                    )
                    
                    if similarity_score > 0.3:
                        similar_docs.append({
                            'document': doc,
                            'similarity_score': similarity_score,
                            'common_topics': await self._find_common_topics(
                                source_metadata,
                                json.loads(doc.metadata) if doc.metadata else {}
                            )
                        })
                except Exception as e:
                    logging.error(f"Error processing similar document {doc.id}: {str(e)}")
                    continue

            # Sort by similarity score
            similar_docs.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similar_docs[:limit]

        except Exception as e:
            logging.error(f"Error finding similar documents: {str(e)}")
            return []

    async def _calculate_document_similarity(self, source_metadata: Dict, target_metadata: Dict) -> float:
        """Calculate similarity between two documents"""
        try:
            # Entity similarity
            source_entities = set(e['name'].lower() for e in source_metadata.get('entities', []))
            target_entities = set(e['name'].lower() for e in target_metadata.get('entities', []))
            
            entity_similarity = len(source_entities & target_entities) / \
                max(len(source_entities | target_entities), 1)

            # Category similarity
            source_categories = set(c.lower() for c in source_metadata.get('categories', []))
            target_categories = set(c.lower() for c in target_metadata.get('categories', []))
            
            category_similarity = len(source_categories & target_categories) / \
                max(len(source_categories | target_categories), 1)

            # Embedding similarity if available
            embedding_similarity = 0.0
            if 'embedding' in source_metadata and 'embedding' in target_metadata:
                source_embedding = np.array(source_metadata['embedding'])
                target_embedding = np.array(target_metadata['embedding'])
                embedding_similarity = cosine_similarity(
                    source_embedding.reshape(1, -1),
                    target_embedding.reshape(1, -1)
                )[0][0]

            # Combine similarities with weights
            final_similarity = (
                0.3 * entity_similarity +
                0.3 * category_similarity +
                0.4 * embedding_similarity
            )

            return min(max(final_similarity, 0.0), 1.0)

        except Exception as e:
            logging.error(f"Error calculating document similarity: {str(e)}")
            return 0.0

    async def _find_common_topics(self, source_metadata: Dict, target_metadata: Dict) -> List[str]:
        """Find common topics between two documents"""
        try:
            common_topics = []
            
            # Compare entities
            source_entities = {e['name'].lower(): e for e in source_metadata.get('entities', [])}
            target_entities = {e['name'].lower(): e for e in target_metadata.get('entities', [])}
            
            for name in set(source_entities.keys()) & set(target_entities.keys()):
                if source_entities[name].get('salience', 0) > 0.1 and \
                   target_entities[name].get('salience', 0) > 0.1:
                    common_topics.append({
                        'topic': name,
                        'type': source_entities[name].get('type', 'UNKNOWN'),
                        'relevance': (
                            source_entities[name].get('salience', 0) +
                            target_entities[name].get('salience', 0)
                        ) / 2
                    })

            # Sort by relevance
            common_topics.sort(key=lambda x: x['relevance'], reverse=True)
            return [topic['topic'] for topic in common_topics[:5]]

        except Exception as e:
            logging.error(f"Error finding common topics: {str(e)}")
            return []
