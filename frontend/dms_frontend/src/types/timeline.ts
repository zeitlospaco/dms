export type TimelineEventType = 'created' | 'modified' | 'deadline' | 'version' | 'category' | 'feedback';

export interface TimelineEvent {
  id: string;
  type: TimelineEventType;
  date: Date;
  description: string;
  metadata?: {
    version?: number;
    category?: string;
    feedback?: string;
    changes?: {
      added: string[];
      removed: string[];
      modified: string[];
    };
  };
}

export interface DocumentTimelineProps {
  events: TimelineEvent[];
}
