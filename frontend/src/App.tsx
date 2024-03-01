import React, { useEffect } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Auth0ProviderWithNavigate from './auth/auth0-provider-with-navigate';
import ProtectedRoute from './auth/protected-route';
import Dashboard from './components/Dashboard';
import { useAuth0 } from '@auth0/auth0-react';

const App: React.FC = () => {
  const { isAuthenticated, loginWithRedirect, isLoading } = useAuth0();

  useEffect(() => {
    if (!isAuthenticated && !isLoading) {
      loginWithRedirect();
    }
  }, [isAuthenticated, isLoading, loginWithRedirect]);

  return (
    <Router>
      <Auth0ProviderWithNavigate>
        <Routes>
          <Route path="/" element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
          </Route>
        </Routes>
      </Auth0ProviderWithNavigate>
    </Router>
  );
};

export default App;
