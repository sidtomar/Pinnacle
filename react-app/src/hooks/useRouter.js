import { useState, useEffect, useCallback } from 'react';

/**
 * Custom hook for hash-based routing
 * Format: #role/page
 * Examples: #medical-affairs/library, #bu-head/analytics
 */
export function useRouter() {
  const [currentRole, setCurrentRole] = useState(() => _getCurrentRole());
  const [currentPage, setCurrentPage] = useState(() => _getCurrentPage());

  const navigate = useCallback((role, page) => {
    window.location.hash = `#${role}/${page}`;
  }, []);

  const navigateTo = useCallback((page) => {
    const role = _getCurrentRole();
    window.location.hash = `#${role}/${page}`;
  }, []);

  useEffect(() => {
    const handleHashChange = () => {
      setCurrentRole(_getCurrentRole());
      setCurrentPage(_getCurrentPage());
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  return {
    currentRole,
    currentPage,
    navigate,
    navigateTo,
    hash: window.location.hash
  };
}

function _getCurrentRole() {
  const hash = window.location.hash.slice(1);
  const [role] = hash.split('/');
  return role || 'medical-affairs';
}

function _getCurrentPage() {
  const hash = window.location.hash.slice(1);
  const [role, page] = hash.split('/');
  if (page) return page;
  return role === 'bu-head' ? 'today' : 'library';
}
