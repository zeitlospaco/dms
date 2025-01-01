import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DocumentList } from './documents/DocumentList';
import { DocumentUploadDialog } from './documents/DocumentUploadDialog';
import { DocumentPreview } from './documents/DocumentPreview';
import { FolderTree } from './folders/FolderTree';
import { CategorySelect } from './categories/CategorySelect';
import { SmartSearch } from './insights/SmartSearch';
import { Document } from '../services/drive';
import { useState } from 'react';

const queryClient = new QueryClient();

export function Dashboard() {
  const [selectedFolderId, setSelectedFolderId] = useState<number>();
  const [selectedCategoryId, setSelectedCategoryId] = useState<number>();
  const [searchValue, setSearchValue] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState<string[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);

  // Smart suggestions based on search input
  const handleSearchChange = (value: string) => {
    setSearchValue(value);
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

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
        <header className="sticky top-0 bg-white/80 backdrop-blur-sm shadow-sm z-50 transition-all duration-300">
          <div className="mx-auto max-w-7xl px-4 py-4">
            <div className="flex items-center justify-between">
              <h1 className="text-3xl font-bold text-gray-900 transition-colors">Document Management System</h1>
              <div className="flex items-center gap-4">
                <button
                  onClick={() => setIsUploadDialogOpen(true)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 hover:shadow-lg"
                >
                  Upload Document
                </button>
                <button
                  onClick={() => {
                    localStorage.removeItem('auth_token');
                    window.location.href = '/login';
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors duration-200"
                >
                  Sign Out
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-6">
          <div className="grid grid-cols-12 gap-6">
            {/* Sidebar */}
            <div className="col-span-3 bg-white rounded-lg shadow">
              <div className="p-4 border-b">
                <h2 className="text-lg font-medium">Folders</h2>
              </div>
              <FolderTree
                onFolderSelect={setSelectedFolderId}
                selectedFolderId={selectedFolderId}
              />
            </div>

            {/* Main content */}
            <div className="col-span-9 space-y-6">
              {/* Search and filters */}
              <div className="bg-white rounded-lg shadow p-4">
                <div className="grid grid-cols-12 gap-4">
                  <div className="col-span-6">
                    <SmartSearch
                      value={searchValue}
                      onChange={handleSearchChange}
                      suggestions={searchSuggestions}
                      onSuggestionClick={setSearchValue}
                    />
                  </div>
                  <div className="col-span-6">
                    <CategorySelect
                      value={selectedCategoryId}
                      onChange={setSelectedCategoryId}
                    />
                  </div>
                </div>
              </div>

              {/* Document list */}
              <div className="bg-white rounded-lg shadow">
                <div className="p-4 border-b">
                  <h2 className="text-lg font-medium">Documents</h2>
                </div>
                <DocumentList
                  folderId={selectedFolderId}
                  categoryId={selectedCategoryId}
                  searchQuery={searchValue}
                  onDocumentClick={setSelectedDocument}
                />
              </div>
            </div>
          </div>
        </main>

        {/* Document Preview Modal */}
        {selectedDocument && (
          <DocumentPreview
            document={selectedDocument}
            onClose={() => setSelectedDocument(null)}
          />
        )}

        {/* Upload dialog */}
        <DocumentUploadDialog
          isOpen={isUploadDialogOpen}
          onClose={() => setIsUploadDialogOpen(false)}
          folderId={selectedFolderId}
          onUploadComplete={() => queryClient.invalidateQueries({ queryKey: ['documents'] })}
        />
      </div>
    </QueryClientProvider>
  );
}
