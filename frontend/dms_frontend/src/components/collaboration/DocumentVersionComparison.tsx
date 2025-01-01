import { useEffect, useState } from 'react';
import { Document, DocumentVersion } from '../../types/document';
import { Card } from '../ui/card';
import { ScrollArea } from '../ui/scroll-area';
import { workflowService } from '../../services/workflow';
import { useToast } from '../../hooks/use-toast';

interface DocumentVersionComparisonProps {
  document: Document;
  version?: number;
}

export function DocumentVersionComparison({ document, version }: DocumentVersionComparisonProps) {
  const [currentVersion, setCurrentVersion] = useState<DocumentVersion | null>(() => null);
  const [previousVersion, setPreviousVersion] = useState<DocumentVersion | null>(() => null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    const loadVersions = async () => {
      try {
        setLoading(true);
        const documentId = typeof document.id === 'string' ? parseInt(document.id, 10) : document.id;
        const versions = await workflowService.getVersions(documentId);
        
        if (versions.length > 0) {
          const targetVersion = version || versions[versions.length - 1].version;
          const currentVer = versions.find(v => v.version === targetVersion) || null;
          const prevVer = versions.find(v => v.version === targetVersion - 1) || null;
          
          setCurrentVersion(() => currentVer);
          setPreviousVersion(() => prevVer);
        }
      } catch (error) {
        console.error('Error loading versions:', error);
        toast({
          title: 'Error loading versions',
          description: 'Failed to load document versions. Please try again.',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    if (document.id) {
      loadVersions();
    }
  }, [document.id, version, toast]);

  const renderChanges = (changes?: { added: string[]; removed: string[]; modified: string[] }) => {
    if (!changes) return null;

    return (
      <div className="space-y-4">
        {changes.added.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-green-600 mb-2">Added Content</h4>
            {changes.added.map((line, index) => (
              <div key={index} className="text-sm bg-green-50 p-2 rounded mb-1">
                + {line}
              </div>
            ))}
          </div>
        )}
        
        {changes.removed.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-red-600 mb-2">Removed Content</h4>
            {changes.removed.map((line, index) => (
              <div key={index} className="text-sm bg-red-50 p-2 rounded mb-1">
                - {line}
              </div>
            ))}
          </div>
        )}
        
        {changes.modified.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-blue-600 mb-2">Modified Content</h4>
            {changes.modified.map((line, index) => (
              <div key={index} className="text-sm bg-blue-50 p-2 rounded mb-1">
                ~ {line}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <Card className="p-4">
      <h3 className="text-lg font-semibold mb-4">Version Comparison</h3>
      {loading ? (
        <div className="text-sm text-gray-500">Loading versions...</div>
      ) : currentVersion ? (
        <ScrollArea className="h-[400px]">
          <div className="space-y-6">
            <div>
              <h4 className="font-medium mb-2">Current Version ({currentVersion.version})</h4>
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="font-medium">Topic:</span>{' '}
                  {currentVersion.metadata.topic || 'None'}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Sentiment:</span>{' '}
                  {currentVersion.metadata.sentiment || 'None'}
                </div>
                <div className="text-sm">
                  <span className="font-medium">Folder:</span>{' '}
                  {currentVersion.metadata.folder}
                </div>
              </div>
              {currentVersion.changes && (
                <div className="mt-4">
                  <h5 className="font-medium mb-2">Changes from Previous Version</h5>
                  {renderChanges(currentVersion.changes)}
                </div>
              )}
            </div>
            {previousVersion && (
              <div>
                <h4 className="font-medium mb-2">Previous Version ({previousVersion.version})</h4>
                <div className="space-y-2">
                  <div className="text-sm">
                    <span className="font-medium">Topic:</span>{' '}
                    {previousVersion.metadata.topic || 'None'}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Sentiment:</span>{' '}
                    {previousVersion.metadata.sentiment || 'None'}
                  </div>
                  <div className="text-sm">
                    <span className="font-medium">Folder:</span>{' '}
                    {previousVersion.metadata.folder}
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>
      ) : (
        <div className="text-sm text-gray-500">No version information available</div>
      )}
    </Card>
  );
}
