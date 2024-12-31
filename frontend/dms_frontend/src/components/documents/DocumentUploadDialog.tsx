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
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [isUploading, setIsUploading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('enable_workflow', 'true');

    try {
      const response = await fetch(
        'https://document-management-app-jbey7enb.devinapps.com/api/documents/upload',
        {
          method: 'POST',
          body: formData,
        }
      );

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      onUpload(selectedFile);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error uploading file');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
    }
  };

  return (
    <div className={`fixed inset-0 bg-black/30 backdrop-blur-sm transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
      <div className={`fixed inset-x-0 top-1/2 -translate-y-1/2 max-w-lg mx-auto p-6 bg-white/95 rounded-lg shadow-xl transition-all duration-300 transform ${isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}`}>
        <h3 className="text-lg font-medium mb-4">Upload Document</h3>
        
        <div className="space-y-4">
          <SmartSearch
            value=""
            onChange={() => {}}
            suggestions={suggestions}
            onSuggestionClick={() => {}}
          />
          
          <div
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer"
            onClick={() => fileInputRef.current?.click()}
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
          >
            <p className="text-sm text-gray-500 mb-2">
              {selectedFile ? selectedFile.name : 'Drag and drop your file here, or click to select'}
            </p>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={handleFileSelect}
            />
          </div>

          {error && (
            <p className="text-sm text-red-600">{error}</p>
          )}
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
            disabled={isUploading}
          >
            Cancel
          </button>
          <button
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className={`px-4 py-2 text-sm text-white rounded-lg ${
              !selectedFile || isUploading
                ? 'bg-blue-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isUploading ? 'Uploading...' : 'Upload'}
          </button>
        </div>
      </div>
    </div>
  );
}
