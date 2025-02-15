import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { initiateOAuth, handleCallback } from '../../services/auth';

export function Login() {
  const history = useHistory();
  const urlParams = new URLSearchParams(window.location.search);

  useEffect(() => {
    const handleAuth = async () => {
      try {
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

        // Check if we're in the callback flow
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        
        if (code && state) {
          // Handle OAuth callback
          await handleCallback(code, state);
          history.push('/dashboard');
        } else {
          // Start new OAuth flow
          console.log('Starting OAuth flow');
          const { auth_url } = await initiateOAuth();
          console.log('Redirecting to Google OAuth');
          window.location.href = auth_url;
        }
      } catch (error) {
        console.error('Authentication error:', error);
        localStorage.removeItem('oauth_state');
        localStorage.removeItem('auth_token');
        history.push('/login?error=auth_failed');
      }
    };

    handleAuth();
  }, [history, urlParams]);

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
