import type { FC } from 'react';

interface DocumentSummaryProps {
  summary: string | null;
  sentiment: {
    label: string | null;
    score: number | null;
  };
  topics: {
    label: string | null;
    confidence: number | null;
  };
}

export function DocumentSummary({ summary, sentiment, topics }: DocumentSummaryProps) {
  if (!summary && !sentiment.label && !topics.label) {
    return null;
  }

  return (
    <div className="space-y-4 p-4 border rounded-lg bg-white/50 backdrop-blur-sm">
      {summary && (
        <div>
          <h4 className="text-sm font-medium mb-2">Summary</h4>
          <p className="text-sm text-gray-600">{summary}</p>
        </div>
      )}
      
      {sentiment.label && (
        <div>
          <h4 className="text-sm font-medium mb-2">Sentiment</h4>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 rounded-full text-xs ${
              sentiment.label === 'positive' ? 'bg-green-100 text-green-800' :
              sentiment.label === 'negative' ? 'bg-red-100 text-red-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {sentiment.label}
            </span>
            {sentiment.score !== null && (
              <span className="text-xs text-gray-500">
                {(sentiment.score * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </div>
      )}

      {topics.label && (
        <div>
          <h4 className="text-sm font-medium mb-2">Main Topic</h4>
          <div className="flex items-center gap-2">
            <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded-full text-xs">
              {topics.label}
            </span>
            {topics.confidence !== null && (
              <span className="text-xs text-gray-500">
                {(topics.confidence * 100).toFixed(0)}%
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
