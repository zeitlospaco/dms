import { useEffect, useState } from 'react';
import { checkHealth } from '../services/api';

export function HealthCheck() {
  const [status, setStatus] = useState<string>('Loading...');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const result = await checkHealth();
        setStatus(`Backend Status: ${result.status}`);
      } catch (err) {
        setError('Failed to connect to backend');
        console.error('Health check error:', err);
      }
    };

    fetchHealth();
  }, []);

  return (
    <div className="p-4 bg-white rounded-lg shadow mb-4">
      {error ? (
        <div className="text-red-500">{error}</div>
      ) : (
        <div className="text-green-500">{status}</div>
      )}
    </div>
  );
}

export default HealthCheck;
