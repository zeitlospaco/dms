import React from 'react';
import { SmartSearch } from '../insights/SmartSearch';
import { driveService } from '@/services/drive';
import { useToast } from '@/hooks/use-toast';

interface DocumentUploadDialogProps {
  isOpen: boolean;
  onClose: () => void;
  folderId?: number;
  onUploadComplete: () => void;
  className?: string;
}

export function DocumentUploadDialog({ isOpen, onClose, folderId, onUploadComplete, className }: DocumentUploadDialogProps) {
  const [suggestions] = React.useState<string[]>([
    'Invoice from Company XYZ',
    'Contract Agreement',
    'Meeting Minutes',
  ]);
  const [selectedFile, setSelectedFile] = React.useState<File | null>(null);
  const [isUploading, setIsUploading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  const { toast } = useToast();
  
  const handleUpload = async () => {
    if (!selectedFile) {
      setError('Please select a file first');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const uncategorizedFolderId = import.meta.env.VITE_UNCATEGORIZED_FOLDER_ID;
      const response = await driveService.uploadDocument(
        selectedFile,
        folderId || parseInt(uncategorizedFolderId)
      );

      console.log('Upload response:', response);
      
      if (response.ai_processing?.category_suggestion) {
        toast({
          title: 'Document categorized',
          description: `Suggested category: ${response.ai_processing.category_suggestion}`,
        });
      }

      toast({
        title: 'Upload successful',
        description: `${selectedFile.name} has been uploaded successfully.`,
      });

      onUploadComplete();
      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Error uploading file';
      setError(errorMessage);
      toast({
        title: 'Upload failed',
        description: errorMessage,
        variant: 'destructive',
      });
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
    <div className={`fixed inset-0 bg-black/30 backdrop-blur-sm transition-opacity duration-300 ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'} ${className || ''}`}>
      <div className={`fixed inset-x-0 top-1/2 -translate-y-1/2 max-w-lg mx-auto p-6 bg-white/95 rounded-lg shadow-xl transition-all duration-300 transform ${isOpen ? 'scale-100 opacity-100' : 'scale-95 opacity-0'}`}>
        <h3 className="text-lg font-medium mb-4">Upload Document</h3>
        
        <div className="space-y-4">
          <SmartSearch
            value={selectedFile?.name || ''}
            onChange={() => {}}
            suggestions={suggestions}
            onSuggestionClick={(_suggestion) => {
              if (fileInputRef.current) {
                fileInputRef.current.value = '';
              }
              setSelectedFile(null);
              setError(null);
            }}
            className="mb-4"
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
