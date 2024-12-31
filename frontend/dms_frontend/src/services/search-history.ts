import api from './api';

export interface SearchHistoryEntry {
  query: string;
  timestamp: string;
  clicked_category?: string;
  clicked_folder?: string;
}

export class SearchHistoryService {
  async updateSearchHistory(query: string): Promise<void> {
    try {
      await api.post('/api/search/history', { query });
    } catch (error) {
      console.error('Failed to update search history:', error);
    }
  }

  async getSearchHistory(): Promise<SearchHistoryEntry[]> {
    try {
      const response = await api.get('/api/search/history');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch search history:', error);
      return [];
    }
  }
}

export const searchHistoryService = new SearchHistoryService();
