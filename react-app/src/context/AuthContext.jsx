import { createContext, useState, useCallback, useEffect } from 'react';

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isLoggedIn, setIsLoggedIn] = useState(() =>
    localStorage.getItem('pinnacle_logged_in') === 'true'
  );
  const [user, setUser] = useState(() =>
    localStorage.getItem('pinnacle_user') || null
  );

  const VALID_ROLES = ['admin', 'bu-head', 'medical-affairs'];

  const [role, setRoleState] = useState(() => {
    const hash = window.location.hash.slice(1);
    const [hashRole] = hash.split('/');
    if (VALID_ROLES.includes(hashRole)) {
      localStorage.setItem('pinnacle_role', hashRole);
      return hashRole;
    }
    const savedRole = localStorage.getItem('pinnacle_role');
    return savedRole || 'admin';
  });

  const defaultPageForRole = (r) => {
    if (r === 'admin') return 'pipeline';
    if (r === 'bu-head') return 'today';
    return 'library';
  };

  // Set hash on initial load if empty (only when logged in)
  useEffect(() => {
    if (!isLoggedIn) return;
    if (!window.location.hash || window.location.hash === '#') {
      window.location.hash = `#${role}/${defaultPageForRole(role)}`;
    }
  }, [isLoggedIn]);

  // Keep role in sync with hash changes
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash.slice(1);
      const [hashRole] = hash.split('/');
      if (VALID_ROLES.includes(hashRole)) {
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

  const login = useCallback((username) => {
    localStorage.setItem('pinnacle_logged_in', 'true');
    localStorage.setItem('pinnacle_user', username);
    // Admin always starts in admin role
    const startRole = 'admin';
    localStorage.setItem('pinnacle_role', startRole);
    setRoleState(startRole);
    setUser(username);
    setIsLoggedIn(true);
    window.location.hash = `#${startRole}/${defaultPageForRole(startRole)}`;
  }, []);

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
    window.location.hash = `#${newRole}/${defaultPageForRole(newRole)}`;
  }, []);

  const isAdmin = role === 'admin';
  const isMA = role === 'medical-affairs';
  const isBUHead = role === 'bu-head';

  const value = {
    isLoggedIn,
    user,
    login,
    logout,
    role,
    setRole,
    isAdmin,
    isMA,
    isBUHead,
    canExport: isBUHead,
    canRunPipeline: isAdmin || isMA,
    canApproveContent: isMA,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
