import { Document } from './document';
import { DocumentTag } from '../services/workflow';

export interface DocumentSummaryProps {
  summary: string | null;
  sentiment: {
    label: string | null;
    score: number | null;
  };
  topics: {
    label: string | null;
    confidence: number | null;
  };
}

export interface SmartTagsProps {
  document: Document;
  onTagClick?: (tag: DocumentTag) => void;
}
