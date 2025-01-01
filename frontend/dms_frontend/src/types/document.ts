export interface Document {
  id: number;
  filename: string;
  mime_type: string;
  size_bytes: number;
  google_drive_id: string;
  created_at: string;
  updated_at: string;
  content?: string;
  folder?: string;
  folder_id?: number;
  extracted_text?: string;
  confidence_score?: number;
  categories: Array<{
    id: number;
    name: string;
    description?: string;
  }>;
  
  // AI-enhanced fields
  summary_text?: string;
  sentiment_label?: 'positive' | 'negative' | 'neutral';
  sentiment_score?: number;
  topic_label?: string;
  topic_confidence?: number;
  deadline_date?: string;
  analysis_date?: string;
  
  // Version control
  version?: number;
  previous_version_id?: string;
  
  // Collaboration
  last_viewed_by?: string;
  view_count?: number;
}

export interface DocumentVersion {
  id?: string;
  document_id: string | number;
  version: number;
  content?: string;
  metadata: {
    topic?: string | null;
    sentiment?: string | null;
    folder: string;
  };
  changes?: {
    added: string[];
    removed: string[];
    modified: string[];
  };
  created_at?: string;
  created_by?: string;
}
