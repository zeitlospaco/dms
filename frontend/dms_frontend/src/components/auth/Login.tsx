import { useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { GoogleLogin } from '@react-oauth/google';
import { handleGoogleLogin } from '../../services/auth';

export function Login() {
  const history = useHistory();
  const urlParams = new URLSearchParams(window.location.search);

  useEffect(() => {
    // Check if we already have an auth token
    const existingToken = localStorage.getItem('auth_token');
    if (existingToken) {
      history.push('/dashboard');
    }
  }, [history]);

  const onSuccess = async (credentialResponse: any) => {
    try {
      const result = await handleGoogleLogin(credentialResponse);
      if (result.token) {
        localStorage.setItem('auth_token', result.token);
        history.push('/dashboard');
      }
    } catch (error) {
      console.error('Authentication error:', error);
      history.push('/login?error=auth_failed');
    }
  };

  const onError = () => {
    console.error('Login Failed');
    history.push('/login?error=auth_failed');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sign in to DMS
          </h2>
          <div className="mt-8 flex justify-center">
            <GoogleLogin
              onSuccess={onSuccess}
              onError={onError}
              useOneTap
            />
          </div>
          {urlParams?.get('error') && (
            <div className="mt-4">
              <p className="text-center text-sm text-red-600">
                Failed to authenticate with Google. Please try again.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Login;
