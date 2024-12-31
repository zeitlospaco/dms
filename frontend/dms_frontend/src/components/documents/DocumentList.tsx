import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Document } from '@/services/drive';
import { driveService } from '@/services/drive';
import { Button } from '@/components/ui/button';
import { FileText, Trash2, MoveRight } from 'lucide-react';

interface DocumentListProps {
  folderId?: number;
  categoryId?: number;
  searchQuery?: string;
  onDocumentClick?: (document: Document) => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ folderId, categoryId, searchQuery, onDocumentClick }) => {
  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents', folderId, categoryId, searchQuery],
    queryFn: () => driveService.searchDocuments(searchQuery || '', categoryId, folderId),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center p-4">
        <div className="animate-pulse flex space-x-4">
          <div className="h-10 w-10 bg-gray-200 rounded-full"></div>
          <div className="flex-1 space-y-4 py-1">
            <div className="h-4 bg-gray-200 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!documents?.length) {
    return <div className="text-center text-gray-500 p-4">No documents found</div>;
  }

  return (
    <div className="divide-y divide-gray-100">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="p-4 hover:bg-gray-50 cursor-pointer transition-colors duration-200"
          onClick={() => onDocumentClick?.(doc)}
        >
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-sm font-medium">{doc.filename}</h3>
              <div className="mt-1 flex items-center gap-2">
                {doc.topic_label && (
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full transition-colors duration-200 hover:bg-blue-200">
                    {doc.topic_label}
                  </span>
                )}
                {doc.sentiment_label && (
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    doc.sentiment_label === 'positive' ? 'bg-green-100 text-green-800' :
                    doc.sentiment_label === 'negative' ? 'bg-red-100 text-red-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {doc.sentiment_label}
                  </span>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <div className="text-xs text-gray-500">
                {new Date(doc.created_at).toLocaleDateString()}
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  driveService.deleteDocument(doc.id);
                }}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  /* Implement move dialog */
                }}
              >
                <MoveRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};
