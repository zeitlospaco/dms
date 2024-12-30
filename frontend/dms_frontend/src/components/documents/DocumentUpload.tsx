import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { driveService } from '@/services/drive';

interface DocumentUploadProps {
  folderId?: number;
  onUploadComplete?: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ folderId, onUploadComplete }) => {
  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    try {
      for (const file of acceptedFiles) {
        await driveService.uploadDocument(file, folderId);
      }
      onUploadComplete?.();
    } catch (error) {
      console.error('Upload failed:', error);
    }
  }, [folderId, onUploadComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
        ${isDragActive ? 'border-primary bg-primary/5' : 'border-gray-300 hover:border-primary'}`}
    >
      <input {...getInputProps()} />
      <Upload className="mx-auto h-12 w-12 text-gray-400" />
      <p className="mt-2 text-sm text-gray-600">
        {isDragActive
          ? 'Drop the files here...'
          : 'Drag and drop files here, or click to select files'}
      </p>
      <Button variant="outline" className="mt-4">
        Select Files
      </Button>
    </div>
  );
};
