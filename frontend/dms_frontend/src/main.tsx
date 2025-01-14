import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { GoogleOAuthProvider } from '@react-oauth/google'
import './index.css'
import App from './App.tsx'

// Debug environment variables and initialization
console.log('Application initialization started');
console.log('Environment Variables:', {
  VITE_API_URL: import.meta.env.VITE_API_URL,
  VITE_GOOGLE_OAUTH_CLIENT_ID: import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID,
  MODE: import.meta.env.MODE,
});

const root = document.getElementById('root');
if (!root) {
  console.error('Root element not found');
} else {
  try {
    console.log('Root element found, attempting to render');
    const app = createRoot(root);
    app.render(
      <StrictMode>
        <GoogleOAuthProvider clientId="701201679988-racsm7mcvro3q8td3k71a6aeu8pr4p1a.apps.googleusercontent.com">
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </GoogleOAuthProvider>
      </StrictMode>,
    );
    console.log('Initial render complete');
  } catch (error) {
    console.error('Error during render:', error);
  }
}
