import React from 'react';
import { SmartSearch } from '../insights/SmartSearch';

interface DocumentUploadDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload: (file: File) => void;
}

export function DocumentUploadDialog({ isOpen, onClose, onUpload }: DocumentUploadDialogProps) {
  const [suggestions] = React.useState<string[]>([
    'Invoice from Company XYZ',
    'Contract Agreement',
    'Meeting Minutes',
  ]);

  return (
    <div className={`fixed inset-0 bg-black/50 ${isOpen ? 'block' : 'hidden'}`}>
      <div className="fixed inset-x-0 top-1/2 -translate-y-1/2 max-w-lg mx-auto p-6 bg-white rounded-lg shadow-xl">
        <h3 className="text-lg font-medium mb-4">Upload Document</h3>
        
        <div className="space-y-4">
          <SmartSearch
            value=""
            onChange={() => {}}
            suggestions={suggestions}
            onSuggestionClick={() => {}}
          />
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
            <p className="text-sm text-gray-500 mb-2">
              Drag and drop your file here, or click to select
            </p>
            <input
              type="file"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  onUpload(file);
                  onClose();
                }
              }}
            />
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
          >
            Cancel
          </button>
          <button
            onClick={() => {}}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Upload
          </button>
        </div>
      </div>
    </div>
  );
}
