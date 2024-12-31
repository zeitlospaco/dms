import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Folder as FolderIcon, ChevronRight, ChevronDown } from 'lucide-react';
import { driveService, Folder } from '@/services/drive';
import { cn } from '@/lib/utils';

interface FolderTreeProps {
  onFolderSelect?: (folderId: number) => void;
  selectedFolderId?: number;
}

interface FolderNodeProps extends FolderTreeProps {
  folder: Folder;
  level: number;
}

const FolderNode: React.FC<FolderNodeProps> = ({ folder, level, onFolderSelect, selectedFolderId }) => {
  const [isExpanded, setIsExpanded] = React.useState(false);

  const hasChildren = folder.children && folder.children.length > 0;
  const isSelected = folder.id === selectedFolderId;

  return (
    <div className="select-none">
      <div
        className={cn(
          'flex items-center py-1 px-2 rounded-md cursor-pointer hover:bg-gray-100',
          isSelected && 'bg-primary/10'
        )}
        style={{ paddingLeft: `${level * 1.5}rem` }}
        onClick={() => onFolderSelect?.(folder.id)}
      >
        {hasChildren ? (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setIsExpanded(!isExpanded);
            }}
            className="p-1 hover:bg-gray-200 rounded-md"
          >
            {isExpanded ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        ) : (
          <span className="w-6" />
        )}
        <FolderIcon className="h-4 w-4 text-yellow-500 mr-2" />
        <span className="text-sm">{folder.name}</span>
      </div>
      {isExpanded && folder.children && (
        <div>
          {folder.children.map((child) => (
            <FolderNode
              key={child.id}
              folder={child}
              level={level + 1}
              onFolderSelect={onFolderSelect}
              selectedFolderId={selectedFolderId}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export const FolderTree: React.FC<FolderTreeProps> = ({ onFolderSelect, selectedFolderId }) => {
  const { data: folders, isLoading } = useQuery({
    queryKey: ['folders'],
    queryFn: driveService.getFolderStructure,
  });

  if (isLoading) {
    return <div className="p-4">Loading folders...</div>;
  }

  if (!folders?.length) {
    return <div className="p-4 text-gray-500">No folders found</div>;
  }

  return (
    <div className="p-2">
      <h3 className="text-sm font-medium mb-3">Folders</h3>
      {folders.map((folder) => (
        <FolderNode
          key={folder.id}
          folder={folder}
          level={0}
          onFolderSelect={onFolderSelect}
          selectedFolderId={selectedFolderId}
        />
      ))}
    </div>
  );
};
