import api from './api';

export interface Version {
  id: string;
  document_id: number;
  version_number: number;
  created_at: string;
  changes: string;
  user_id: string;
}

export const versionService = {
  async getVersions(documentId: number): Promise<Version[]> {
    const response = await api.get(`/api/versions/${documentId}`);
    return response.data;
  },

  async createVersion(documentId: number, changes: string): Promise<Version> {
    const response = await api.post(`/api/versions`, {
      document_id: documentId,
      changes,
    });
    return response.data;
  },

  async restoreVersion(documentId: number, versionNumber: number, userId: string): Promise<void> {
    await api.post(`/api/versions/${documentId}/restore`, {
      version_number: versionNumber,
      user_id: userId,
    });
  },

  async compareVersions(
    documentId: number,
    version1: number,
    version2: number
  ): Promise<{ diff: string[] }> {
    const response = await api.get(`/api/versions/${documentId}/compare`, {
      params: { version1, version2 },
    });
    return response.data;
  },
};
