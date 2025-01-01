import { useEffect, useState } from 'react';
import { Card } from '../ui/card';
import { Document } from '../../types/document';
import { workflowService } from '../../services/workflow';
import { useToast } from '../../hooks/use-toast';

interface TimelineEvent {
  id: string;
  type: 'created' | 'modified' | 'deadline' | 'version' | 'comment';
  date: Date;
  description: string;
  details?: string;
}

interface DocumentTimelineProps {
  document: Document;
}

export function DocumentTimeline({ document }: DocumentTimelineProps) {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const loadTimeline = async () => {
      try {
        setLoading(true);
        const documentId = typeof document.id === 'string' ? parseInt(document.id, 10) : document.id;
        const updates = await workflowService.getDocumentUpdates(documentId);
        const versions = await workflowService.getVersions(documentId);
        
        const baseEvents: TimelineEvent[] = [
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
          }
        ];

        const deadlineEvent: TimelineEvent[] = document.deadline_date ? [{
          id: 'deadline',
          type: 'deadline' as const,
          date: new Date(document.deadline_date),
          description: 'Deadline'
        }] : [];

        const versionEvents: TimelineEvent[] = versions.map(version => ({
          id: `version-${version.version}`,
          type: 'version' as const,
          date: new Date(document.updated_at),
          description: `Version ${version.version}`,
          details: `Changes: ${Object.keys(version.metadata).join(', ')}`
        }));

        const updateEvents: TimelineEvent[] = updates ? [{
          id: 'update',
          type: 'modified' as const,
          date: new Date(),
          description: 'Document updated',
          details: `Changes: ${updates.topic ? 'Topic, ' : ''}${updates.sentiment ? 'Sentiment' : ''}`
        }] : [];
        const allEvents: TimelineEvent[] = [
          ...baseEvents,
          ...deadlineEvent,
          ...versionEvents,
          ...updateEvents
        ].sort((a, b) => b.date.getTime() - a.date.getTime());

        setEvents(allEvents);
      } catch (error) {
        console.error('Error loading timeline:', error);
        toast({
          title: 'Error loading timeline',
          description: 'Failed to load document timeline. Please try again.',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    if (document.id) {
      loadTimeline();
    }
  }, [document.id, document.created_at, document.updated_at, document.deadline_date, toast]);

  const getEventColor = (type: TimelineEvent['type']) => {
    switch (type) {
      case 'created':
        return 'bg-green-100 text-green-800';
      case 'modified':
        return 'bg-blue-100 text-blue-800';
      case 'deadline':
        return 'bg-red-100 text-red-800';
      case 'version':
        return 'bg-purple-100 text-purple-800';
      case 'comment':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <Card className="p-4">
      <h3 className="text-lg font-semibold mb-3">Document Timeline</h3>
      {loading ? (
        <div className="text-sm text-gray-500">Loading timeline...</div>
      ) : events.length > 0 ? (
        <div className="space-y-4">
          {events.map((event) => (
            <div
              key={event.id}
              className={`p-3 rounded-lg ${getEventColor(event.type)}`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-medium">{event.description}</h4>
                  {event.details && (
                    <p className="text-sm mt-1">{event.details}</p>
                  )}
                </div>
                <time className="text-sm">
                  {event.date.toLocaleDateString()}
                </time>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-sm text-gray-500">No timeline events available</div>
      )}
    </Card>
  );
}
