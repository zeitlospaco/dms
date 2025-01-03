import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';

export function Login() {
  const history = useHistory();

  useEffect(() => {
    // Check if we have an auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      history.push('/');
      return;
    }

    // Start Google OAuth flow
    const backendUrl = import.meta.env.VITE_API_URL || 'https://app-frgtiqwl-blue-grass-9650.fly.dev';
    const loginUrl = `${backendUrl}/api/v1/auth/google/url`;
    
    fetch(loginUrl)
      .then(response => response.json())
      .then(data => {
        if (data.auth_url) {
          window.location.href = data.auth_url;
        }
      })
      .catch(error => {
        console.error('Failed to get auth URL:', error);
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
