import React from 'react';
import { DocumentSummary } from '../insights/DocumentSummary';
import { DocumentTimeline } from '../collaboration/DocumentTimeline';

interface DocumentPreviewProps {
  document: {
    id: number;
    filename: string;
    created_at: string;
    updated_at: string;
    summary_text: string | null;
    sentiment_label: string | null;
    sentiment_score: number | null;
    topic_label: string | null;
    topic_confidence: number | null;
    deadline_date: string | null;
  };
}

export function DocumentPreview({ document }: DocumentPreviewProps) {
  const timelineEvents = [
    {
      id: 'created',
      type: 'created' as const,
      date: new Date(document.created_at),
      description: 'Document created'
    },
    {
      id: 'updated',
      type: 'modified' as const,
      date: new Date(document.updated_at),
      description: 'Last modified'
    },
    ...(document.deadline_date ? [{
      id: 'deadline',
      type: 'deadline' as const,
      date: new Date(document.deadline_date),
      description: 'Deadline'
    }] : [])
  ];

  return (
    <div className="space-y-6 p-4">
      <div>
        <h3 className="text-lg font-medium mb-4">{document.filename}</h3>
        
        <DocumentSummary
          summary={document.summary_text}
          sentiment={{
            label: document.sentiment_label,
            score: document.sentiment_score
          }}
          topics={{
            label: document.topic_label,
            confidence: document.topic_confidence
          }}
        />
      </div>

      <DocumentTimeline events={timelineEvents} />
    </div>
  );
}
