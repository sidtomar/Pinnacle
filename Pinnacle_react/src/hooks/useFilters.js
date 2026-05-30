import { useMemo, useCallback, useState } from 'react';

/**
 * Hook for filtering and sorting data
 */
export function useFilters(data = [], initialFilters = {}) {
  const [filters, setFiltersState] = useState({
    search: '',
    specialty: [],
    therapyArea: [],
    tags: [],
    dateRange: { start: null, end: null },
    ...initialFilters
  });

  const [sorting, setSortingState] = useState({
    field: 'date',
    direction: 'desc'
  });

  const applyFilter = useCallback((filterKey, value) => {
    setFiltersState(prev => ({
      ...prev,
      [filterKey]: value
    }));
  }, []);

  const removeFilter = useCallback((filterKey) => {
    setFiltersState(prev => {
      const newFilters = { ...prev };
      if (Array.isArray(prev[filterKey])) {
        newFilters[filterKey] = [];
      } else if (filterKey === 'dateRange') {
        newFilters[filterKey] = { start: null, end: null };
      } else {
        newFilters[filterKey] = '';
      }
      return newFilters;
    });
  }, []);

  const clearFilters = useCallback(() => {
    setFiltersState({
      search: '',
      specialty: [],
      therapyArea: [],
      tags: [],
      dateRange: { start: null, end: null }
    });
  }, []);

  const setSorting = useCallback((field, direction = 'asc') => {
    setSortingState({ field, direction });
  }, []);

  const filteredData = useMemo(() => {
    let result = [...data];

    // Text search
    if (filters.search) {
      const q = filters.search.toLowerCase();
      result = result.filter(item =>
        (item.title?.toLowerCase().includes(q)) ||
        (item.summary?.toLowerCase().includes(q)) ||
        (item.authors?.toLowerCase().includes(q))
      );
    }

    // Specialty filter
    if (filters.specialty?.length > 0) {
      result = result.filter(item =>
        filters.specialty.includes(item.specialty)
      );
    }

    // Therapy area filter
    if (filters.therapyArea?.length > 0) {
      result = result.filter(item =>
        filters.therapyArea.includes(item.therapy_area)
      );
    }

    // Tags filter
    if (filters.tags?.length > 0) {
      result = result.filter(item => {
        const itemTags = item.tags || [];
        return filters.tags.some(tag => itemTags.includes(tag));
      });
    }

    // Date range filter
    if (filters.dateRange?.start || filters.dateRange?.end) {
      result = result.filter(item => {
        const itemDate = new Date(item.publication_date || item.created_at);
        if (filters.dateRange.start && itemDate < new Date(filters.dateRange.start)) {
          return false;
        }
        if (filters.dateRange.end && itemDate > new Date(filters.dateRange.end)) {
          return false;
        }
        return true;
      });
    }

    // Sorting
    const { field, direction } = sorting;
    result.sort((a, b) => {
      let aVal = a[field];
      let bVal = b[field];

      if (aVal < bVal) return direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return direction === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [data, filters, sorting]);

  return {
    filters,
    setFilters: setFiltersState,
    applyFilter,
    removeFilter,
    clearFilters,
    sorting,
    setSorting,
    filteredData,
    totalResults: filteredData.length
  };
}
