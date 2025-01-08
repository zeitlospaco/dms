import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import api from '../../services/api';

export function Login() {
  const history = useHistory();
  const urlParams = new URLSearchParams(window.location.search);

  useEffect(() => {
    // Check for authentication errors
    const error = urlParams.get('error');
    if (error) {
      console.error('Authentication error:', error);
      localStorage.removeItem('oauth_state');
      localStorage.removeItem('auth_token');
      return;
    }

    // Check if we already have an auth token
    const existingToken = localStorage.getItem('auth_token');
    if (existingToken) {
      history.push('/dashboard');
      return;
    }

    // If no error and no token, start OAuth flow
    const state = Math.random().toString(36).substring(7) + Math.random().toString(36).substring(7);
    localStorage.setItem('oauth_state', state);

    // Start Google OAuth flow using configured API instance
    api.get('/auth/login', { params: { state } })
      .then(response => {
        if (response.data.auth_url) {
          console.log('Starting OAuth flow with state:', state);
          window.location.href = response.data.auth_url;
        }
      })
      .catch(error => {
        console.error('Failed to get auth URL:', error);
        localStorage.removeItem('oauth_state');
        localStorage.removeItem('auth_token');
      });
  }, [history]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          {urlParams?.get('error') ? (
            <div>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-red-600">
                Authentication Error
              </h2>
              <p className="mt-2 text-center text-sm text-gray-600">
                {urlParams.get('error') === 'auth_failed' ? 
                  'Failed to authenticate with Google. Please try again.' :
                  'An error occurred during authentication. Please try again.'}
              </p>
              <button
                onClick={() => {
                  localStorage.removeItem('oauth_state');
                  window.location.href = '/login';
                }}
                className="mt-4 w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Try Again
              </button>
            </div>
          ) : (
            <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
              Redirecting to login...
            </h2>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;
