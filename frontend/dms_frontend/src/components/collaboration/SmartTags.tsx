import { useEffect, useState } from 'react';
import { Badge } from '../ui/badge';
import { Card } from '../ui/card';
import { Document } from '../../services/drive';
import { DocumentTag, workflowService } from '../../services/workflow';
import { useToast } from '../../hooks/use-toast';

interface SmartTagsProps {
  document: Document;
  onTagClick?: (tag: DocumentTag) => void;
}

export function SmartTags({ document, onTagClick }: SmartTagsProps) {
  const [tags, setTags] = useState<DocumentTag[]>([]);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  // Convert size_bytes to human readable format
  const formatSize = (bytes: number) => {
    const units = ['B', 'KB', 'MB', 'GB'];
    let size = bytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024;
      unitIndex++;
    }
    return `${size.toFixed(1)} ${units[unitIndex]}`;
  };

  useEffect(() => {
    const loadTags = async () => {
      try {
        setLoading(true);
        // Convert string ID to number for API call
        const documentId = typeof document.id === 'string' ? parseInt(document.id, 10) : document.id;
        const suggestedTags = await workflowService.getSuggestedTags(documentId);
        
        const baseTags: DocumentTag[] = [
          ...(document.topic_label ? [{ label: document.topic_label, type: 'topic' as const }] : []),
          ...(document.sentiment_label ? [{ label: document.sentiment_label, type: 'sentiment' as const }] : []),
          ...(document.deadline_date ? [{ label: 'Has Deadline', type: 'deadline' as const }] : [])
        ];
        setTags([...baseTags, ...suggestedTags]);
      } catch (error) {
        console.error('Error loading tags:', error);
        toast({
          title: 'Error loading tags',
          description: 'Failed to load smart tags. Please try again.',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    if (document.id) {
      loadTags();
    }
  }, [document.id, document.topic_label, document.sentiment_label, document.deadline_date, toast]);

  const getTagColor = (type: DocumentTag['type']) => {
    switch (type) {
      case 'topic':
        return 'bg-blue-100 text-blue-800 hover:bg-blue-200';
      case 'sentiment':
        return document.sentiment_label === 'positive'
          ? 'bg-green-100 text-green-800 hover:bg-green-200'
          : document.sentiment_label === 'negative'
          ? 'bg-red-100 text-red-800 hover:bg-red-200'
          : 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200';
      case 'keyword':
        return 'bg-purple-100 text-purple-800 hover:bg-purple-200';
      case 'deadline':
        return 'bg-red-100 text-red-800 hover:bg-red-200';
      default:
        return 'bg-gray-100 text-gray-800 hover:bg-gray-200';
    }
  };

  return (
    <Card className="p-4">
      <h3 className="text-lg font-semibold mb-3">Smart Tags</h3>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="text-gray-500">Size:</div>
          <div>{formatSize(document.size_bytes)}</div>
          <div className="text-gray-500">Created:</div>
          <div>{new Date(document.created_at).toLocaleString()}</div>
          <div className="text-gray-500">Modified:</div>
          <div>{new Date(document.updated_at).toLocaleString()}</div>
        </div>
        
        <div className="flex flex-wrap gap-2">
          {loading ? (
            <div className="text-sm text-gray-500">Loading tags...</div>
          ) : tags.length > 0 ? (
            tags.map((tag, index) => (
              <Badge
                key={`${tag.type}-${index}`}
                className={`cursor-pointer transition-colors ${getTagColor(tag.type)}`}
                onClick={() => onTagClick?.(tag)}
              >
                {tag.label}
              </Badge>
            ))
          ) : (
            <div className="text-sm text-gray-500">No tags available</div>
          )}
        </div>
      </div>
    </Card>
  );
}
