// src/App.tsx
import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import LoginButton from './components/LoginButton';
import LogoutButton from './components/LogoutButton';

const App: React.FC = () => {
  const { isAuthenticated, user } = useAuth0();

  return (
    <div>
      {isAuthenticated ? (
        <>
          <p>Welcome, {user?.name}!</p>
          <LogoutButton />
        </>
      ) : (
        <LoginButton />
      )}
    </div>
  );
};

export default App;
