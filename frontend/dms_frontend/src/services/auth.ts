import api from './api';

export interface TokenResponse {
  token: string;
}

export const handleGoogleLogin = async (credentialResponse: { credential?: string }) => {
  try {
    if (!credentialResponse.credential) {
      throw new Error('No credential received from Google');
    }

    console.log('Sending credential to backend for verification');
    const response = await api.post('/api/v1/auth/verify', {
      credential: credentialResponse.credential
    });
    
    console.log('Backend verification response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Failed to verify Google credentials:', error);
    throw error;
  }
};

// Remove handleCallback as it's now handled entirely by the backend

export const refreshToken = async () => {
  try {
    const response = await api.get('/api/v1/auth/refresh');
    return response.data;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    throw error;
  }
};
