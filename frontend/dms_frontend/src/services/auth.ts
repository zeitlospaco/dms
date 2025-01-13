import api from './api';

export interface AuthResponse {
  auth_url: string;
  state: string;
}

export interface TokenResponse {
  token: string;
}

export const initiateOAuth = async () => {
  try {
    // Generate a random state parameter for CSRF protection
    const randomBytes = new Uint8Array(16);
    window.crypto.getRandomValues(randomBytes);
    const state = Array.from(randomBytes, byte => byte.toString(16).padStart(2, '0')).join('');
    
    console.log('Generating state parameter:', state);
    
    // Store state in localStorage for validation after redirect
    localStorage.setItem('oauth_state', state);
    
    // Use backend URL for OAuth callback
    const clientId = import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID;
    const backendUrl = import.meta.env.VITE_API_URL || 'https://app-frgtiqwl-blue-grass-9650.fly.dev';
    const redirectUri = `${backendUrl}/api/v1/auth/callback`;
    console.log('Using redirect URI:', redirectUri);
    const scope = encodeURIComponent([
      'https://www.googleapis.com/auth/drive',
      'https://www.googleapis.com/auth/drive.file',
      'https://www.googleapis.com/auth/drive.metadata.readonly',
      'https://www.googleapis.com/auth/drive.metadata',
      'https://www.googleapis.com/auth/drive.readonly',
      'https://www.googleapis.com/auth/drive.photos.readonly',
      'https://www.googleapis.com/auth/drive.apps.readonly',
      'https://www.googleapis.com/auth/drive.appdata',
      'https://www.googleapis.com/auth/drive.meet.readonly',
      'https://www.googleapis.com/auth/drive.scripts'
    ].join(' '));
    
    const authUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
      `client_id=${encodeURIComponent(clientId)}&` +
      `redirect_uri=${encodeURIComponent(redirectUri)}&` +
      `response_type=code&` +
      `scope=${scope}&` +
      `access_type=offline&` +
      `state=${state}&` +
      `prompt=consent`;
    
    console.log('Generated auth URL:', authUrl);
    
    return { auth_url: authUrl, state };
  } catch (error) {
    console.error('Failed to initiate OAuth:', error);
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
