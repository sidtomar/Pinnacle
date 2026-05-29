import { useState, useCallback, useEffect } from 'react';
import { api } from '../services/api';

/**
 * Hook for making API calls with loading/error states
 * Usage:
 *   const { data, loading, error, refetch } = useApi('/content');
 *   const { mutate, loading } = useApi('/content', 'POST');
 */
export function useApi(endpoint, method = 'GET', autoFetch = true) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const refetch = useCallback(async (payload = null) => {
    setLoading(true);
    setError(null);
    try {
      let response;
      switch (method.toUpperCase()) {
        case 'GET':
          response = await api.get(endpoint);
          break;
        case 'POST':
          response = await api.post(endpoint, payload);
          break;
        case 'PUT':
          response = await api.put(endpoint, payload);
          break;
        case 'DELETE':
          response = await api.delete(endpoint);
          break;
        default:
          throw new Error(`Unsupported method: ${method}`);
      }
      setData(response.data);
      return response.data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [endpoint, method]);

  const mutate = useCallback(async (payload) => {
    return refetch(payload);
  }, [refetch]);

  // Auto-fetch on mount if GET request
  useEffect(() => {
    if (autoFetch && method === 'GET') {
      refetch();
    }
  }, [endpoint, method, autoFetch, refetch]);

  return {
    data,
    loading,
    error,
    refetch,
    mutate
  };
}
