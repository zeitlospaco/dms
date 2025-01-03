import React, { useEffect, useState } from 'react';
import { Version, versionService } from '../../services/versions.ts';
import { format } from 'date-fns';
import { Button } from '../ui/button';
import { useToast } from '../../hooks/use-toast';

interface VersionHistoryProps {
  documentId: string;
  userId: string;
  onVersionRestored?: () => void;
}

export const VersionHistory: React.FC<VersionHistoryProps> = ({
  documentId,
  userId,
  onVersionRestored
}) => {
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedVersions, setSelectedVersions] = useState<[number?, number?]>([]);
  const [comparison, setComparison] = useState<any>(null);
  const { toast } = useToast();

  useEffect(() => {
    loadVersions();
  }, [documentId]);

  const loadVersions = async () => {
    try {
      const data = await versionService.getVersions(Number(documentId));
      setVersions(data);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load version history',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRestore = async (versionNumber: number) => {
    try {
      await versionService.restoreVersion(Number(documentId), versionNumber, userId);
      toast({
        title: 'Success',
        description: `Restored to version ${versionNumber}`,
      });
      loadVersions();
      onVersionRestored?.();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to restore version',
        variant: 'destructive'
      });
    }
  };

  const handleCompare = async () => {
    if (selectedVersions[0] && selectedVersions[1]) {
      try {
        const data = await versionService.compareVersions(
          Number(documentId),
          selectedVersions[0],
          selectedVersions[1]
        );
        setComparison(data);
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to compare versions',
          variant: 'destructive'
        });
      }
    }
  };

  const handleVersionSelect = (versionNumber: number) => {
    setSelectedVersions(prev => {
      if (prev[0] === versionNumber) {
        return [undefined, prev[1]];
      }
      if (prev[1] === versionNumber) {
        return [prev[0], undefined];
      }
      if (!prev[0]) {
        return [versionNumber, prev[1]];
      }
      if (!prev[1]) {
        return [prev[0], versionNumber];
      }
      return [versionNumber, undefined];
    });
  };

  if (loading) {
    return <div>Loading version history...</div>;
  }

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">Version History</h3>
      
      <div className="space-y-2">
        {versions.map((version) => (
          <div
            key={version.id}
            className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50"
          >
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={selectedVersions.includes(version.version_number)}
                onChange={() => handleVersionSelect(version.version_number)}
                className="rounded border-gray-300"
              />
              <div>
                <div className="font-medium">
                  Version {version.version_number}
                </div>
                <div className="text-sm text-gray-500">
                  {format(new Date(version.created_at), 'PPpp')}
                </div>
                {version.changes && (
                  <div className="text-sm text-gray-600">
                    {version.changes}
                  </div>
                )}
              </div>
            </div>
            
            <Button
              onClick={() => handleRestore(version.version_number)}
              variant="outline"
              size="sm"
            >
              Restore
            </Button>
          </div>
        ))}
      </div>

      {selectedVersions[0] && selectedVersions[1] && (
        <Button onClick={handleCompare} className="mt-4">
          Compare Selected Versions
        </Button>
      )}

      {comparison && (
        <div className="mt-4 p-4 border rounded-lg">
          <h4 className="font-medium mb-2">Version Comparison</h4>
          <pre className="text-sm bg-gray-50 p-3 rounded overflow-x-auto">
            {comparison.diff.map((line: string, index: number) => (
              <div
                key={index}
                className={`${
                  line.startsWith('+')
                    ? 'text-green-600'
                    : line.startsWith('-')
                    ? 'text-red-600'
                    : ''
                }`}
              >
                {line}
              </div>
            ))}
          </pre>
        </div>
      )}
    </div>
  );
};
