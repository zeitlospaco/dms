import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { driveService } from '@/services/drive';
import { workflowService } from '@/services/workflow';
import { useToast } from '@/hooks/use-toast';

interface DocumentUploadProps {
  folderId?: number;
  onUploadComplete?: () => void;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({ folderId, onUploadComplete }) => {
  const [isUploading, setIsUploading] = useState(false);
  const { toast } = useToast();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setIsUploading(true);
    try {
      for (const file of acceptedFiles) {
        // Upload document
        const response = await driveService.uploadDocument(file, folderId);
        const document = response.document;

        // Process through workflow
        await workflowService.processDocument(document.id);
        
        // Check for duplicates
        const duplicates = await workflowService.getDuplicates(document.id);
        if (duplicates.length > 0) {
          toast({
            title: 'Potential duplicates found',
            description: `Found ${duplicates.length} similar document(s). Please review.`,
            variant: 'destructive',
          });
        }

        toast({
          title: 'Document uploaded',
          description: `${file.name} has been processed and categorized.`,
        });
      }
      onUploadComplete?.();
    } catch (error) {
      console.error('Upload failed:', error);
      toast({
        title: 'Upload failed',
        description: 'There was an error uploading your document.',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  }, [folderId, onUploadComplete, toast]);

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
      <Button variant="outline" className="mt-4" disabled={isUploading}>
        {isUploading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Processing...
          </>
        ) : (
          'Select Files'
        )}
      </Button>
    </div>
  );
};
