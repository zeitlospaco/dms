import React from 'react';
import { Input } from '../ui/Input';

interface SmartSearchProps {
  value: string;
  onChange: (value: string) => void;
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
}

export function SmartSearch({ 
  value, 
  onChange, 
  suggestions, 
  onSuggestionClick 
}: SmartSearchProps) {
  return (
    <div className="relative">
      <Input
        type="text"
        placeholder="Search documents..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full"
      />
      
      {suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white rounded-lg shadow-lg border p-2 z-10">
          <div className="text-xs font-medium text-gray-500 mb-2">
            Smart Suggestions
          </div>
          <div className="space-y-1">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => onSuggestionClick(suggestion)}
                className="w-full text-left px-2 py-1 text-sm rounded hover:bg-gray-100"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
