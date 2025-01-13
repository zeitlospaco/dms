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
    
    // Get auth URL from backend
    const response = await api.get(`/api/v1/auth/login?state=${state}`);
    console.log('Received auth URL from backend:', response.data.auth_url);
    return response.data;
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
