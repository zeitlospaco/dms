import React from 'react';
import { Document } from '../../types/document';
import { Button } from '../ui/button';
import { FileText, Download, ExternalLink } from 'lucide-react';
import { CategoryBadge } from '../categories/CategoryBadge';
import { FeedbackForm } from '../feedback/FeedbackForm';
import { DocumentTag } from '../../services/workflow';

import { DocumentSummary } from '../insights/DocumentSummary';
import { DocumentTimeline } from '../collaboration/DocumentTimeline';
import { DocumentVersionComparison } from '../collaboration/DocumentVersionComparison';
import { RelatedDocuments } from '../insights/RelatedDocuments';
import { SmartTags } from '../collaboration/SmartTags';

interface DocumentPreviewProps {
  document: Document;
  onClose: () => void;
}

export const DocumentPreview: React.FC<DocumentPreviewProps> = ({ document, onClose }) => {
  const isPreviewable = document.mime_type.startsWith('image/') || 
                       document.mime_type === 'application/pdf';

  // Timeline events are now handled by the DocumentTimeline component

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
        
        <div className="flex-1 overflow-auto p-4 space-y-4">
          {document.categories.length > 0 && (
            <div className="flex flex-wrap gap-2 pb-4">
              {document.categories.map((category) => (
                <CategoryBadge key={category.id} category={{ ...category, id: category.id.toString() }} />
              ))}
            </div>
          )}
          
          {/* Document Summary and Analysis */}
          <DocumentSummary
            summary={document.summary_text || null}
            sentiment={{
              label: document.sentiment_label || null,
              score: document.sentiment_score || null
            }}
            topics={{
              label: document.topic_label || null,
              confidence: document.topic_confidence || null
            }}
          />

          {/* Document Timeline */}
          <DocumentTimeline document={document} />
          
          {/* Document Version Comparison */}
          <DocumentVersionComparison document={document} />
          
          {/* Related Documents */}
          <RelatedDocuments 
            documentId={String(document.id)}
            onDocumentSelect={(id) => {
              console.log('Selected related document:', id);
              // TODO: Implement document selection logic
            }}
          />
          
          {/* Smart Tags */}
          <SmartTags
            document={document}
            onTagClick={(tag: DocumentTag) => {
              console.log('Tag clicked:', tag);
              // TODO: Implement tag click logic
            }}
          />
          
          {/* Document Preview */}
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

        {document.categories.length > 0 && (
          <div className="p-4 border-t border-b">
            <FeedbackForm
              documentId={document.id}
              currentCategory={document.categories[0].name}
              onFeedbackSubmitted={() => {
                // Optionally refresh document data after feedback
              }}
            />
          </div>
        )}
        
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
