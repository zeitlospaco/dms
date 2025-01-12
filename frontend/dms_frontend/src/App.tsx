import { useState, useEffect } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Switch, Route, Redirect } from 'react-router-dom';
import { Login } from './components/auth/Login';
import { DocumentList } from './components/documents/DocumentList';
import { DocumentUploadDialog } from './components/documents/DocumentUploadDialog';
import { DocumentPreview } from './components/documents/DocumentPreview';
import { FolderTree } from './components/folders/FolderTree';
import { CategorySelect } from './components/categories/CategorySelect';
import { SmartSearch } from './components/insights/SmartSearch';
import { HealthCheck } from './components/HealthCheck';
import type { Document } from '@/types/document';
import { handleCallback, type TokenResponse } from './services/auth';

const queryClient = new QueryClient();

function App() {
  const [selectedFolderId, setSelectedFolderId] = useState<number>();
  const [selectedCategoryId, setSelectedCategoryId] = useState<number>();
  const [searchValue, setSearchValue] = useState('');
  const [searchSuggestions, setSearchSuggestions] = useState<string[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);

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

  const isAuthenticated = !!localStorage.getItem('auth_token');

  const DashboardContent = () => (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="mx-auto max-w-7xl px-4 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Document Management System</h1>
            <button
              onClick={() => setIsUploadDialogOpen(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Upload Document
            </button>
          </div>
        </div>
        <HealthCheck />
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
        onUpload={(file) => console.log('File uploaded:', file)}
        onUploadComplete={() => queryClient.invalidateQueries({ queryKey: ['documents'] })}
      />
    </div>
  );

  // Handle token storage in Login component instead
  const location = window.location;
  const urlParams = new URLSearchParams(location.search);
  const error = urlParams.get('error');

  useEffect(() => {
    if (error) {
      // Clear any existing token on error
      localStorage.removeItem('auth_token');
    }
  }, [error]);

  return (
    <QueryClientProvider client={queryClient}>
      <Switch>
        <Route path="/login">
          {isAuthenticated ? <Redirect to="/dashboard" /> : <Login />}
        </Route>
        <Route path="/callback">
          {() => {
            const params = new URLSearchParams(window.location.search);
            const code = params.get('code');
            const state = params.get('state');
            const error = params.get('error');
            
            console.log('OAuth callback received:', { code: !!code, state: !!state, error });
            
            if (error) {
              localStorage.removeItem('oauth_state');
              localStorage.removeItem('auth_token');
              return <Redirect to={`/login?error=${error}`} />;
            }
            
            if (code && state) {
              // Handle the callback in the frontend
              handleCallback(code, state)
                .then((response: TokenResponse) => {
                  localStorage.setItem('auth_token', response.token);
                  window.location.href = '/dashboard';
                })
                .catch((error) => {
                  console.error('Failed to handle callback:', error);
                  return <Redirect to={`/login?error=auth_failed`} />;
                });
              return <div>Processing authentication...</div>;
            }
            
            return <Redirect to="/login?error=invalid_callback" />;
          }}
        </Route>
        <Route path="/dashboard">
          {isAuthenticated ? <DashboardContent /> : <Redirect to="/login" />}
        </Route>
        <Route path="/">
          <Redirect to={isAuthenticated ? "/dashboard" : "/login"} />
        </Route>
      </Switch>
    </QueryClientProvider>
  );
}

export default App;
