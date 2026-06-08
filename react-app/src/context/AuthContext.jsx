import { createContext, useState, useCallback, useEffect } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(() =>
    localStorage.getItem('pinnacle_logged_in') === 'true'
  );
  const [user, setUser] = useState(() =>
    localStorage.getItem('pinnacle_user') || null
  );

  const [role, setRoleState] = useState(() => {
    const hash = window.location.hash.slice(1);
    const [hashRole] = hash.split('/');
    if (hashRole === 'medical-affairs' || hashRole === 'bu-head') {
      localStorage.setItem('pinnacle_role', hashRole);
      return hashRole;
    }
    const savedRole = localStorage.getItem('pinnacle_role');
    return savedRole || 'bu-head';
  });

  // Set hash on initial load if empty (only when logged in)
  useEffect(() => {
    if (!isLoggedIn) return;
    if (!window.location.hash || window.location.hash === '#') {
      const defaultPage = role === 'bu-head' ? 'today' : 'library';
      window.location.hash = `#${role}/${defaultPage}`;
    }
  }, [isLoggedIn]);

  // Keep role in sync with hash changes
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

  const login = useCallback((email) => {
    localStorage.setItem('pinnacle_logged_in', 'true');
    localStorage.setItem('pinnacle_user', email);
    setUser(email);
    setIsLoggedIn(true);
    const defaultPage = role === 'bu-head' ? 'today' : 'library';
    window.location.hash = `#${role}/${defaultPage}`;
  }, [role]);

  const logout = useCallback(() => {
    localStorage.removeItem('pinnacle_logged_in');
    localStorage.removeItem('pinnacle_user');
    setUser(null);
    setIsLoggedIn(false);
    window.location.hash = '';
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
    isLoggedIn,
    user,
    login,
    logout,
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
