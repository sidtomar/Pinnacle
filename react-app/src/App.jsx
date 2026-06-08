import React from 'react';
import { AuthProvider } from './context/AuthContext';
import { AppProvider } from './context/AppContext';
import { ContentProvider } from './context/ContentContext';
import AppLayout from './components/layouts/AppLayout';
import LoginScreen from './components/pages/LoginScreen';
import { useAuth } from './hooks/useAuth';

function AppInner() {
  const { isLoggedIn } = useAuth();
  if (!isLoggedIn) return <LoginScreen />;
  return (
    <AppProvider>
      <ContentProvider>
        <AppLayout />
      </ContentProvider>
    </AppProvider>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppInner />
    </AuthProvider>
  );
}
