import api from './api';

export interface FeedbackRequest {
  document_id: number;
  correct_category: string;
  comment?: string;
}

export const feedbackService = {
  submitFeedback: async (feedback: FeedbackRequest) => {
    const response = await api.post('/feedback', feedback);
    return response.data;
  },
};
