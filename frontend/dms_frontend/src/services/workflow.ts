import api from './api';

export interface DocumentTag {
  id: string;
  name: string;
  type: string;
  confidence: number;
}

export const workflowService = {
  async getTags(documentId: number): Promise<DocumentTag[]> {
    const response = await api.get(`/api/workflow/tags/${documentId}`);
    return response.data;
  },

  async addTag(documentId: number, tag: Partial<DocumentTag>): Promise<DocumentTag> {
    const response = await api.post(`/api/workflow/tags`, {
      document_id: documentId,
      ...tag,
    });
    return response.data;
  },
};
