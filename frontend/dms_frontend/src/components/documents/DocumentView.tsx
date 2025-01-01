import React from 'react';
import { VersionHistory } from '../versions/VersionHistory';
import { Button } from '../ui/button';
import { useToast } from '../../hooks/use-toast';
import { versionService } from '../../services/versions';

interface DocumentViewProps {
  documentId: string;
  userId: string;
  onVersionChange?: () => void;
}

export const DocumentView: React.FC<DocumentViewProps> = ({
  documentId,
  userId,
  onVersionChange
}) => {
  const { toast } = useToast();
  const [showVersionHistory, setShowVersionHistory] = React.useState(false);

  const handleCreateVersion = async () => {
    try {
      await versionService.createVersion(documentId, {
        user_id: userId,
        comment: 'Manual version created'
      });
      toast({
        title: 'Success',
        description: 'New version created successfully'
      });
      onVersionChange?.();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create version',
        variant: 'destructive'
      });
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Button
          onClick={() => setShowVersionHistory(!showVersionHistory)}
          variant="outline"
        >
          {showVersionHistory ? 'Hide Version History' : 'Show Version History'}
        </Button>
        <Button onClick={handleCreateVersion}>
          Create New Version
        </Button>
      </div>

      {showVersionHistory && (
        <VersionHistory
          documentId={documentId}
          userId={userId}
          onVersionRestored={onVersionChange}
        />
      )}
    </div>
  );
};
