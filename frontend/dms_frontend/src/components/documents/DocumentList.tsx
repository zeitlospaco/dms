import React from 'react';
import { DocumentPreview } from './DocumentPreview';

interface Document {
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
}

export function DocumentList() {
  const [documents, setDocuments] = React.useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = React.useState<Document | null>(null);

  React.useEffect(() => {
    // TODO: Fetch documents from API
    // This is a placeholder for demonstration
    setDocuments([
      {
        id: 1,
        filename: 'Example Document.pdf',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        summary_text: 'This is an example document summary showing AI-powered features.',
        sentiment_label: 'positive',
        sentiment_score: 0.85,
        topic_label: 'Business',
        topic_confidence: 0.92,
        deadline_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      },
    ]);
  }, []);

  return (
    <div className="divide-y">
      {documents.map((doc) => (
        <div
          key={doc.id}
          className="p-4 hover:bg-gray-50 cursor-pointer"
          onClick={() => setSelectedDocument(doc)}
        >
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-sm font-medium">{doc.filename}</h3>
              <div className="mt-1 flex items-center gap-2">
                {doc.topic_label && (
                  <span className="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded-full">
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
            <div className="text-xs text-gray-500">
              {new Date(doc.created_at).toLocaleDateString()}
            </div>
          </div>
          
          {selectedDocument?.id === doc.id && (
            <div className="mt-4">
              <DocumentPreview document={doc} />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
