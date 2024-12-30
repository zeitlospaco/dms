import React from 'react';
import { Document } from '@/services/drive';
import { Button } from '@/components/ui/Button';
import { FileText, Download, ExternalLink } from 'lucide-react';

interface DocumentPreviewProps {
  document: Document;
  onClose: () => void;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({ document, onClose }) => {
  const isPreviewable = document.mime_type.startsWith('image/') || 
                       document.mime_type === 'application/pdf';

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg w-full max-w-4xl max-h-[90vh] flex flex-col">
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-2">
            <FileText className="text-blue-500" />
            <h2 className="text-lg font-medium">{document.filename}</h2>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ×
          </Button>
        </div>
        
        <div className="flex-1 overflow-auto p-4">
          {isPreviewable ? (
            <iframe
              src={`https://drive.google.com/file/d/${document.google_drive_id}/preview`}
              className="w-full h-full min-h-[400px] border-0"
              title={document.filename}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full space-y-4">
              <FileText className="h-16 w-16 text-gray-400" />
              <p className="text-gray-600">Preview not available for this file type</p>
            </div>
          )}
        </div>

        <div className="p-4 border-t flex justify-end space-x-2">
          <Button
            variant="outline"
            onClick={() => window.open(`https://drive.google.com/uc?export=download&id=${document.google_drive_id}`)}
          >
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          <Button
            onClick={() => window.open(`https://drive.google.com/file/d/${document.google_drive_id}`)}
          >
            <ExternalLink className="h-4 w-4 mr-2" />
            Open in Drive
          </Button>
        </div>
      </div>
    </div>
  );
};
