import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import Auth0ProviderWithHistory from './Auth0Provider';

const rootElement = document.getElementById('root');
if (rootElement) {
  createRoot(rootElement).render(
    <Auth0ProviderWithHistory>
      <App />
    </Auth0ProviderWithHistory>
  );
}
