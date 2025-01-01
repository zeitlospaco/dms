import { useState, useEffect } from 'react';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { Search, Loader2 } from 'lucide-react';
import { searchService, type SearchSuggestion, type SearchResult } from '../../services/search';
import { searchHistoryService } from '../../services/search-history';
import { useDebounce } from '../../hooks/use-debounce';
import { RelatedDocuments } from './RelatedDocuments';
import { ErrorMessage } from '../ui/error-message';

interface SmartSearchProps {
  value: string;
  onChange: (value: string) => void;
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
  className?: string;
  onResultsChange?: (results: SearchResult[]) => void;
}

export function SmartSearch({ value, onChange, suggestions: externalSuggestions, onSuggestionClick, className, onResultsChange }: SmartSearchProps) {
  const [internalValue, setInternalValue] = useState(value);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  
  // Merge external suggestions with API suggestions
  const mergedSuggestions = [...suggestions];
  if (externalSuggestions?.length) {
    mergedSuggestions.push(
      ...externalSuggestions.map(suggestion => ({
        text: suggestion,
        type: 'term' as const,
        confidence: 1,
      }))
    );
  }
  const [results, setResults] = useState<SearchResult[]>([]);
  // Display results in the UI or pass to parent component
  useEffect(() => {
    onResultsChange?.(results);
  }, [results, onResultsChange]);
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);
  const debouncedValue = useDebounce(internalValue, 300);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (debouncedValue.length < 2) {
        setSuggestions([]);
        return;
      }
      try {
        const newSuggestions = await searchService.getSuggestions(debouncedValue);
        setSuggestions(newSuggestions);
      } catch (error) {
        console.error('Failed to fetch suggestions:', error);
        setSuggestions([]);
      }
    };
    fetchSuggestions();
  }, [debouncedValue]);

  const handleSearch = async () => {
    if (!value.trim()) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const searchResults = await searchService.searchDocuments(value);
      setResults(searchResults);
      onResultsChange?.(searchResults);
      await searchHistoryService.updateSearchHistory(value);
    } catch (error) {
      console.error('Search failed:', error);
      setError('Failed to search documents. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = async (suggestion: SearchSuggestion) => {
    setInternalValue(suggestion.text);
    onChange(suggestion.text);
    
    if (suggestion.type === 'external') {
      onSuggestionClick(suggestion.text);
    }
    setSuggestions([]);
    if (suggestion.document_id) {
      setSelectedDocument(suggestion.document_id);
    }
    await handleSearch();
  };

  return (
    <div className={`relative ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <div className="flex gap-2">
            <Input
              type="text"
              placeholder="Search documents using natural language..."
              value={internalValue}
              onChange={(e) => {
                setInternalValue(e.target.value);
                onChange(e.target.value);
              }}
              className="w-full"
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              disabled={isLoading}
            />
            <Button onClick={handleSearch} disabled={isLoading} variant="default" size="default">
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
            </Button>
          </div>

          {error && (
            <ErrorMessage message={error} />
          )}

          {suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border p-2 z-10">
              <div className="text-xs font-medium text-gray-500 mb-2">
                Smart Suggestions
              </div>
              <div className="space-y-1">
                {mergedSuggestions.map((suggestion, index) => (
                  <button
                    key={index}
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full text-left px-2 py-1 text-sm rounded hover:bg-gray-100 flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-2">
                      <span>{suggestion.text}</span>
                      {suggestion.type === 'category' && (
                        <span className="text-xs text-blue-500">Category Match</span>
                      )}
                      {suggestion.type === 'term' && (
                        <span className="text-xs text-green-500">Content Match</span>
                      )}
                      {suggestion.type === 'document' && (
                        <span className="text-xs text-purple-500">Document Match</span>
                      )}
                    </div>
                    <div className="flex items-center space-x-2 text-xs text-gray-500">
                      <span className="px-1.5 py-0.5 rounded-full bg-gray-100 group-hover:bg-gray-200">
                        {Math.round(suggestion.confidence * 100)}% Match
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className="md:col-span-1">
          {selectedDocument && (
            <RelatedDocuments
              documentId={selectedDocument}
              className="mt-4 md:mt-0"
              onDocumentSelect={(docId: string) => {
                setSelectedDocument(docId);
                setInternalValue('');
                onChange('');
                setSuggestions([]);
              }}
            />
          )}
        </div>
      </div>
    </div>
  );
}
