import api from './api';
import { Document } from './drive';

export interface SearchSuggestion {
  text: string;
  type: 'category' | 'term' | 'document';
  confidence: number;
  document_id?: string;
}

export interface DocumentWithMetadata extends Document {
  name?: string;
  content?: string;
  category?: string;
  last_accessed?: string;
}

export interface SearchResult {
  document: DocumentWithMetadata;
  score: number;
  highlights: string[];
  is_personalized?: boolean;
}

export interface RelatedDocument {
  document: Document;
  similarity_score: number;
}

export class SearchService {
  async searchDocuments(query: string): Promise<SearchResult[]> {
    try {
      const response = await api.get('/api/search', {
        params: { query }
      });
      return response.data;
    } catch (error) {
      console.error('Search request failed:', error);
      throw new Error('Failed to search documents');
    }
  }

  async getSuggestions(query: string): Promise<SearchSuggestion[]> {
    try {
      const response = await api.get('/api/search/suggestions', {
        params: { query }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
      throw new Error('Failed to fetch search suggestions');
    }
  }

  async getRelatedDocuments(documentId: string): Promise<RelatedDocument[]> {
    try {
      const response = await api.get(`/api/search/related/${documentId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch related documents:', error);
      throw new Error('Failed to fetch related documents');
    }
  }
}

export const searchService = new SearchService();
