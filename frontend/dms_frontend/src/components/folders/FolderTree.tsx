import React from 'react';

interface Folder {
  id: number;
  name: string;
  children: Folder[];
}

export function FolderTree() {
  const [folders, setFolders] = React.useState<Folder[]>([]);
  const [expandedFolders, setExpandedFolders] = React.useState<Set<number>>(new Set());

  React.useEffect(() => {
    // TODO: Fetch folders from API
    // This is a placeholder for demonstration
    setFolders([
      {
        id: 1,
        name: 'Documents',
        children: [
          {
            id: 2,
            name: 'Invoices',
            children: [],
          },
          {
            id: 3,
            name: 'Contracts',
            children: [],
          },
        ],
      },
    ]);
  }, []);

  const toggleFolder = (folderId: number) => {
    setExpandedFolders((prev) => {
      const next = new Set(prev);
      if (next.has(folderId)) {
        next.delete(folderId);
      } else {
        next.add(folderId);
      }
      return next;
    });
  };

  const renderFolder = (folder: Folder, depth: number = 0) => {
    const isExpanded = expandedFolders.has(folder.id);

    return (
      <div key={folder.id} style={{ paddingLeft: `${depth * 1.5}rem` }}>
        <button
          onClick={() => toggleFolder(folder.id)}
          className="flex items-center gap-2 w-full px-2 py-1 hover:bg-gray-100 rounded text-left"
        >
          <span className="text-gray-500">
            {folder.children.length > 0 ? (
              isExpanded ? '▼' : '▶'
            ) : '•'}
          </span>
          <span className="text-sm">{folder.name}</span>
        </button>
        
        {isExpanded && folder.children.map((child) => renderFolder(child, depth + 1))}
      </div>
    );
  };

  return (
    <div className="space-y-1">
      <h3 className="text-sm font-medium mb-3">Folders</h3>
      {folders.map((folder) => renderFolder(folder))}
    </div>
  );
}
