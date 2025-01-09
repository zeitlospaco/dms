import api from './api';

export interface AuthResponse {
  auth_url: string;
  state: string;
}

export const initiateOAuth = async () => {
  try {
    // Generate a random state parameter for CSRF protection
    const randomBytes = new Uint8Array(16);
    window.crypto.getRandomValues(randomBytes);
    const state = Array.from(randomBytes, byte => byte.toString(16).padStart(2, '0')).join('');
    
    // Get the frontend URL for the redirect_uri
    const redirect_uri = import.meta.env.VITE_GOOGLE_OAUTH_REDIRECT_URI;
    
    // Request auth URL from backend
    const response = await api.get<AuthResponse>('/auth/login', {
      params: {
        state,
        redirect_uri
      }
    });
    
    // Store state in localStorage for validation after redirect
    localStorage.setItem('oauth_state', state);
    
    return response.data;
  } catch (error) {
    console.error('Failed to initiate OAuth:', error);
    throw error;
  }
};

export const handleCallback = async (code: string, state: string) => {
  try {
    // Verify state parameter matches the one we stored
    const storedState = localStorage.getItem('oauth_state');
    if (!storedState || state !== storedState) {
      throw new Error('Invalid state parameter');
    }
    
    // Clear stored state
    localStorage.removeItem('oauth_state');
    
    // Exchange code for token
    const response = await api.get('/auth/callback', {
      params: { code, state }
    });
    
    return response.data;
  } catch (error) {
    console.error('Failed to handle OAuth callback:', error);
    throw error;
  }
};

export const refreshToken = async () => {
  try {
    const response = await api.get('/auth/refresh');
    return response.data;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    throw error;
  }
};
