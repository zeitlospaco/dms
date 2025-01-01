import { searchService } from '../../services/search';
import { useQuery } from '@tanstack/react-query';
import { Document } from '@/services/drive';

interface RelatedDocument {
  document: Document;
  similarity_score: number;
}

interface RelatedDocumentsProps {
  documentId: string;
  className?: string;
  onDocumentSelect?: (documentId: string) => void;
}

export function RelatedDocuments({ documentId, className, onDocumentSelect }: RelatedDocumentsProps) {
  const { data: relatedDocs, isLoading } = useQuery({
    queryKey: ['relatedDocuments', documentId],
    queryFn: () => searchService.getRelatedDocuments(documentId),
    enabled: !!documentId,
  });

  if (isLoading) {
    return (
      <div className="p-4 border rounded-lg bg-white/50 backdrop-blur-sm">
        <h3 className="text-sm font-medium text-gray-900 mb-2">Related Documents</h3>
        <div className="space-y-2 animate-pulse">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-6 bg-gray-200 rounded w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (!relatedDocs?.length) {
    return null;
  }

  return (
    <div className={`p-4 border rounded-lg bg-white/50 backdrop-blur-sm ${className || ''}`}>
      <h3 className="text-sm font-medium text-gray-900 mb-2">Related Documents</h3>
      <div className="space-y-2">
        {relatedDocs.map((item: RelatedDocument) => (
          <div
            key={item.document.id}
            className="flex items-center justify-between p-2 rounded-md hover:bg-gray-50 transition-colors cursor-pointer"
            onClick={() => onDocumentSelect?.(String(item.document.id))}
          >
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {item.document.filename}
              </p>
              <p className="text-xs text-gray-500">
                {item.document.categories?.[0]?.name}
              </p>
            </div>
            <div className="ml-2">
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                {Math.round(item.similarity_score * 100)}% match
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
