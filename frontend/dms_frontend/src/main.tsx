import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import { Toaster } from '@/components/ui/toaster'
import { ErrorBoundary } from '@/components/ui/error-boundary'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <App />
        <Toaster />
      </BrowserRouter>
    </ErrorBoundary>
  </StrictMode>,
)
