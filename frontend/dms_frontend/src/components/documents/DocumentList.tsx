import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Document } from '@/services/drive';
import { driveService } from '@/services/drive';
import { Button } from '@/components/ui/Button';
import { FileText, Trash2, MoveRight } from 'lucide-react';

interface DocumentListProps {
  folderId?: number;
  categoryId?: number;
  searchQuery?: string;
}

export const DocumentList: React.FC<DocumentListProps> = ({ folderId, categoryId, searchQuery }) => {
  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents', folderId, categoryId, searchQuery],
    queryFn: () => driveService.searchDocuments(searchQuery || '', categoryId, folderId),
  });

  if (isLoading) {
    return <div className="flex justify-center p-4">Loading documents...</div>;
  }

  if (!documents?.length) {
    return <div className="text-center text-gray-500 p-4">No documents found</div>;
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="flex items-center justify-between p-4 bg-white rounded-lg shadow hover:shadow-md transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <FileText className="text-blue-500" />
            <div>
              <h3 className="font-medium">{doc.filename}</h3>
              <p className="text-sm text-gray-500">
                {new Date(doc.created_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          <div className="flex space-x-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => window.open(`https://drive.google.com/file/d/${doc.google_drive_id}`)}
            >
              View
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => driveService.deleteDocument(doc.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {/* Implement move dialog */}}
            >
              <MoveRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
};
