import React from 'react';
import { AuthProvider } from './context/AuthContext';
import { AppProvider } from './context/AppContext';
import { ContentProvider } from './context/ContentContext';
import AppLayout from './components/layouts/AppLayout';

export default function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <ContentProvider>
          <AppLayout />
        </ContentProvider>
      </AppProvider>
    </AuthProvider>
  );
}
