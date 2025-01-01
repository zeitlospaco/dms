import api from './api';

export interface Document {
  id: number;
  filename: string;
  google_drive_id: string;
  mime_type: string;
  size_bytes: number;
  folder_id?: number;
  extracted_text?: string;
  confidence_score?: number;
  categories: Category[];
  created_at: string;
  updated_at: string;
  topic_label?: string;
  sentiment_label?: 'positive' | 'negative' | 'neutral';
  deadline_date?: string;
  folder?: string;
}

export interface Folder {
  id: number;
  name: string;
  drive_id: string;
  parent_id?: number;
  children?: Folder[];
}

export interface Category {
  id: number;
  name: string;
  description?: string;
}

export interface UploadResponse {
  document: Document;
  ai_processing?: {
    category_suggestion?: string;
    confidence_score?: number;
    folder_suggestion?: {
      id: number;
      name: string;
    };
  };
}

export const driveService = {
  // Document operations
  uploadDocument: async (file: File, folderId?: number, categoryName?: string): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    if (folderId) formData.append('folder_id', folderId.toString());
    if (categoryName) formData.append('category_name', categoryName);

    const response = await api.post<UploadResponse>('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getDocument: async (id: number): Promise<Document> => {
    const response = await api.get<Document>(`/documents/${id}`);
    return response.data;
  },

  deleteDocument: async (id: number): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },

  moveDocument: async (id: number, newFolderId: number): Promise<Document> => {
    const response = await api.patch<Document>(`/documents/${id}/move`, { folder_id: newFolderId });
    return response.data;
  },

  // Folder operations
  getFolderStructure: async (): Promise<Folder[]> => {
    const response = await api.get<Folder[]>('/folders');
    return response.data;
  },

  searchDocuments: async (query: string, categoryId?: number, folderId?: number): Promise<Document[]> => {
    const params = new URLSearchParams();
    params.append('q', query);
    if (categoryId) params.append('category_id', categoryId.toString());
    if (folderId) params.append('folder_id', folderId.toString());

    const response = await api.get<Document[]>(`/documents/search?${params.toString()}`);
    return response.data;
  },
};
