import { createContext, useState, useCallback, useEffect } from 'react';

export const AppContext = createContext();

function _getPageFromHash() {
  const hash = window.location.hash.slice(1);
  const [role, page] = hash.split('/');
  if (page) return page;
  return role === 'bu-head' ? 'today' : 'library';
}

export function AppProvider({ children }) {
  const [currentTab, setCurrentTabState] = useState(() => _getPageFromHash());

  // Sync currentTab with hash changes
  useEffect(() => {
    const onHashChange = () => setCurrentTabState(_getPageFromHash());
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [notifications, setNotifications] = useState([]);
  const [sortField, setSortFieldState] = useState('date');
  const [sortDirection, setSortDirectionState] = useState('asc');
  const [filters, setFiltersState] = useState({
    specialty: [],
    therapyArea: [],
    dateRange: { start: null, end: null },
    tags: [],
    search: ''
  });

  const setCurrentTab = useCallback((tab) => {
    setCurrentTabState(tab);
  }, []);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen(prev => !prev);
  }, []);

  const setSorting = useCallback((field, direction) => {
    setSortFieldState(field);
    setSortDirectionState(direction);
  }, []);

  const setFilters = useCallback((newFilters) => {
    setFiltersState(prev => ({ ...prev, ...newFilters }));
  }, []);

  const clearFilters = useCallback(() => {
    setFiltersState({
      specialty: [],
      therapyArea: [],
      dateRange: { start: null, end: null },
      tags: [],
      search: ''
    });
  }, []);

  const addNotification = useCallback((message, type = 'info', duration = 3000) => {
    const id = Date.now();
    const notification = { id, message, type };
    setNotifications(prev => [...prev, notification]);

    if (duration > 0) {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== id));
      }, duration);
    }

    return id;
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  const value = {
    currentTab,
    setCurrentTab,
    sidebarOpen,
    toggleSidebar,
    selectedDoctor,
    setSelectedDoctor,
    notifications,
    addNotification,
    removeNotification,
    sortField,
    sortDirection,
    setSorting,
    filters,
    setFilters,
    clearFilters
  };

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  );
}
