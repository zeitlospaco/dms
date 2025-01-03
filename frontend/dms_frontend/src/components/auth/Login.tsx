import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export function Login() {
  const navigate = useNavigate();

  useEffect(() => {
    // Check if we have an auth token
    const token = localStorage.getItem('auth_token');
    if (token) {
      navigate('/');
      return;
    }

    // Redirect to backend auth endpoint
    const backendUrl = import.meta.env.VITE_API_URL;
    window.location.href = `${backendUrl}/auth/login`;
  }, [navigate]);

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
