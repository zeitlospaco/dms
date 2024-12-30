import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { DocumentList } from './components/documents/DocumentList';
import { DocumentUpload } from './components/documents/DocumentUpload';
import { DocumentPreview } from './components/documents/DocumentPreview';
import { FolderTree } from './components/folders/FolderTree';
import { CategorySelect } from './components/categories/CategorySelect';
import { Input } from './components/ui/input';
import { Search } from 'lucide-react';
import { Document } from './services/drive';

const queryClient = new QueryClient();

function App() {
  const [selectedFolderId, setSelectedFolderId] = useState<number>();
  const [selectedCategoryId, setSelectedCategoryId] = useState<number>();
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);

  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="mx-auto max-w-7xl px-4 py-6">
            <h1 className="text-3xl font-bold text-gray-900">Document Management System</h1>
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
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                      <Input
                        type="text"
                        placeholder="Search documents..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <div className="col-span-6">
                    <CategorySelect
                      value={selectedCategoryId}
                      onChange={setSelectedCategoryId}
                    />
                  </div>
                </div>
              </div>

              {/* Upload area */}
              <DocumentUpload
                folderId={selectedFolderId}
                onUploadComplete={() => queryClient.invalidateQueries({ queryKey: ['documents'] })}
              />

              {/* Document list */}
              <div className="bg-white rounded-lg shadow">
                <div className="p-4 border-b">
                  <h2 className="text-lg font-medium">Documents</h2>
                </div>
                <DocumentList
                  folderId={selectedFolderId}
                  categoryId={selectedCategoryId}
                  searchQuery={searchQuery}
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
      </div>
    </QueryClientProvider>
  );
}

export default App
