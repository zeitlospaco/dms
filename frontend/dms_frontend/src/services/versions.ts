import api from './api';

export interface Version {
  id: number;
  document_id: string;
  version_number: number;
  created_by: string;
  created_at: string;
  comment?: string;
  metadata: string;
}

export interface VersionCreate {
  user_id: string;
  comment?: string;
}

export interface VersionComparison {
  diff: string[];
  metadata_changes: {
    from: Record<string, any>;
    to: Record<string, any>;
  };
}

export const versionService = {
  createVersion: async (documentId: string, data: VersionCreate): Promise<Version> => {
    const response = await api.post(`/api/versions/${documentId}`, data);
    return response.data;
  },

  getVersions: async (documentId: string): Promise<Version[]> => {
    const response = await api.get(`/api/versions/${documentId}`);
    return response.data;
  },

  restoreVersion: async (documentId: string, versionNumber: number, userId: string): Promise<Version> => {
    const response = await api.post(`/api/versions/${documentId}/restore/${versionNumber}`, { user_id: userId });
    return response.data;
  },

  compareVersions: async (
    documentId: string,
    version1: number,
    version2: number
  ): Promise<VersionComparison> => {
    const response = await api.get(`/api/versions/${documentId}/compare`, {
      params: { version1, version2 }
    });
    return response.data;
  }
};
