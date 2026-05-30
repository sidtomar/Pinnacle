import { createContext, useState, useCallback, useEffect } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [role, setRoleState] = useState(() => {
    // If hash already has a role, use that
    const hash = window.location.hash.slice(1);
    const [hashRole] = hash.split('/');
    if (hashRole === 'medical-affairs' || hashRole === 'bu-head') {
      localStorage.setItem('pinnacle_role', hashRole);
      return hashRole;
    }
    const savedRole = localStorage.getItem('pinnacle_role');
    return savedRole || 'bu-head';
  });

  // Set hash on initial load if empty
  useEffect(() => {
    if (!window.location.hash || window.location.hash === '#') {
      const defaultPage = role === 'bu-head' ? 'today' : 'library';
      window.location.hash = `#${role}/${defaultPage}`;
    }
  }, []);

  // Keep role in sync with hash changes (browser back/forward, URL navigation)
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      const [hashRole] = hash.split('/');
      if (hashRole === 'medical-affairs' || hashRole === 'bu-head') {
        setRoleState(prev => {
          if (prev !== hashRole) {
            localStorage.setItem('pinnacle_role', hashRole);
            return hashRole;
          }
          return prev;
        });
      }
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const setRole = useCallback((newRole) => {
    setRoleState(newRole);
    localStorage.setItem('pinnacle_role', newRole);
    const defaultPage = newRole === 'bu-head' ? 'today' : 'library';
    window.location.hash = `#${newRole}/${defaultPage}`;
  }, []);

  const canExport = role === 'bu-head';
  const canRunPipeline = role === 'medical-affairs';
  const canApproveContent = role === 'medical-affairs';

  const value = {
    role,
    setRole,
    canExport,
    canRunPipeline,
    canApproveContent,
    isMA: role === 'medical-affairs',
    isBUHead: role === 'bu-head'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
