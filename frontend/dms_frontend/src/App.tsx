import React, { useState } from 'react';
import { DocumentList } from './components/documents/DocumentList';
import { DocumentUploadDialog } from './components/documents/DocumentUploadDialog';
import { SmartSearch } from './components/insights/SmartSearch';
import { FolderTree } from './components/folders/FolderTree';

export default function App() {
  const [searchValue, setSearchValue] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState<string[]>([]);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);

  // Simulated smart suggestions based on search input
  const handleSearchChange = (value: string) => {
    setSearchValue(value);
    // In a real implementation, this would call an API to get smart suggestions
    if (value) {
      setSearchSuggestions([
        `Documents related to "${value}"`,
        `Recent files about "${value}"`,
        `Similar topics to "${value}"`,
      ]);
    } else {
      setSearchSuggestions([]);
    }
  };

  const handleUpload = async (file: File) => {
    // TODO: Implement file upload with workflow processing
    console.log('Uploading file:', file.name);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Document Management System</h1>
          <button
            onClick={() => setIsUploadDialogOpen(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Upload Document
          </button>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar with folder tree */}
          <div className="col-span-3">
            <div className="bg-white p-4 rounded-lg shadow">
              <FolderTree />
            </div>
          </div>

          {/* Main content */}
          <div className="col-span-9 space-y-6">
            {/* Search bar with smart suggestions */}
            <div className="w-full">
              <SmartSearch
                value={searchValue}
                onChange={handleSearchChange}
                suggestions={searchSuggestions}
                onSuggestionClick={setSearchValue}
              />
            </div>

            {/* Document list */}
            <div className="bg-white rounded-lg shadow">
              <DocumentList />
            </div>
          </div>
        </div>

        {/* Upload dialog */}
        <DocumentUploadDialog
          isOpen={isUploadDialogOpen}
          onClose={() => setIsUploadDialogOpen(false)}
          onUpload={handleUpload}
        />
      </div>
    </div>
  );
}
