import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { initiateOAuth } from '../../services/auth';

export function Login() {
  const history = useHistory();
  const urlParams = new URLSearchParams(window.location.search);

  useEffect(() => {
    const handleAuth = async () => {
      try {
        // Check for authentication errors
        const authError = urlParams.get('error');
        if (authError) {
          console.error('Authentication error:', authError);
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

        // Start new OAuth flow
        console.log('Starting new OAuth flow');
        try {
          // Clear any existing OAuth state
          localStorage.removeItem('oauth_state');
          localStorage.removeItem('auth_token');
          
          const { auth_url } = await initiateOAuth();
          console.log('Received auth URL:', auth_url);
          
          // Parse and validate the auth URL
          const authUrlObj = new URL(auth_url);
          console.log('Parsed auth URL:', authUrlObj.toString());
          
          // Ensure the redirect URI is using the backend URL
          const redirectUri = import.meta.env.VITE_BACKEND_URL + '/api/v1/auth/callback';
          authUrlObj.searchParams.set('redirect_uri', redirectUri);
          console.log('Updated redirect URI:', redirectUri);
          
          // Navigate to the modified auth URL
          window.location.href = authUrlObj.toString();
        } catch (error) {
          console.error('Failed to initiate OAuth:', error);
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
