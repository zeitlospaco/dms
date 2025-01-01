import api from './api';
import type { Document } from '../types/document';

export interface WorkflowResponse {
  status: string;
  message: string;
  target_folder?: string;
}

export interface DuplicateInfo {
  document: Document;
  similarity_score: number;
  similarity_factors: string[];
}

import { DocumentVersion } from '../types/document';

export interface DocumentTag {
  label: string;
  type: 'topic' | 'sentiment' | 'keyword' | 'deadline';
}

export interface DocumentUpdate {
  version: number;
  topic: string | null;
  sentiment: string | null;
  tags: DocumentTag[];
}

export const workflowService = {
  processDocument: async (documentId: number): Promise<WorkflowResponse> => {
    const response = await api.post<WorkflowResponse>(`/workflow/process/${documentId}`);
    return response.data;
  },

  getDuplicates: async (documentId: number): Promise<DuplicateInfo[]> => {
    const response = await api.get<DuplicateInfo[]>(`/workflow/duplicates/${documentId}`);
    return response.data;
  },

  routeDocument: async (documentId: number): Promise<WorkflowResponse> => {
    const response = await api.post<WorkflowResponse>(`/workflow/route/${documentId}`);
    return response.data;
  },

  getVersions: async (documentId: number): Promise<DocumentVersion[]> => {
    const response = await api.get<DocumentVersion[]>(`/workflow/versions/${documentId}`);
    return response.data;
  },

  getSuggestedTags: async (documentId: number): Promise<DocumentTag[]> => {
    const response = await api.get<{ tags: DocumentTag[] }>(`/workflow/tags/suggest/${documentId}`);
    return response.data.tags;
  },

  getDocumentUpdates: async (documentId: number): Promise<DocumentUpdate> => {
    const response = await api.get<DocumentUpdate>(`/workflow/updates/${documentId}`);
    return response.data;
  }
};
