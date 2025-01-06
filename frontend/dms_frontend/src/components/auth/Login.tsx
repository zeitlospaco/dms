import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import api from '../../services/api';

export function Login() {
  const history = useHistory();

  useEffect(() => {
    // Check if we have an auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      history.push('/');
      return;
    }

    // Generate a random state parameter for OAuth security
    const state = Math.random().toString(36).substring(7);
    localStorage.setItem('oauth_state', state);

    // Start Google OAuth flow using configured API instance
    api.get('/auth/login', { params: { state } })
      .then(response => {
        if (response.data.auth_url) {
          window.location.href = response.data.auth_url;
        }
      })
      .catch(error => {
        console.error('Failed to get auth URL:', error);
        // Clear state on error
        localStorage.removeItem('oauth_state');
      });
  }, [history]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Redirecting to login...
          </h2>
        </div>
      </div>
    </div>
  );
}

export default Login;
