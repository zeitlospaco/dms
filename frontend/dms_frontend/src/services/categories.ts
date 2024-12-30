import api from './api';
import { Category } from './drive';

export const categoryService = {
  getCategories: async (): Promise<Category[]> => {
    const response = await api.get<Category[]>('/categories');
    return response.data;
  },

  createCategory: async (name: string, description?: string): Promise<Category> => {
    const response = await api.post<Category>('/categories', { name, description });
    return response.data;
  },

  trainCategory: async (categoryId: number, documentIds: number[]): Promise<void> => {
    await api.post(`/categories/${categoryId}/train`, { document_ids: documentIds });
  },

  suggestCategory: async (text: string): Promise<{ suggested_category: string; confidence_score: number }> => {
    const response = await api.get('/categories/suggest', { params: { text } });
    return response.data;
  },
};
