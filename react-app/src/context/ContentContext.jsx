import { createContext, useState, useCallback, useEffect } from 'react';
import { api } from '../services/api';

export const ContentContext = createContext();

export function ContentProvider({ children }) {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentId, setCurrentIdState] = useState(null);
  const [currentTags, setCurrentTags] = useState([]);
  const [currentRelevance, setCurrentRelevance] = useState(null);

  // Fetch all papers on mount
  useEffect(() => {
    fetchContent();
  }, []);

  const fetchContent = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.content.list();
      setPapers(Array.isArray(response.data) ? response.data : response.data.papers || []);
    } catch (err) {
      setError(err.message);
      console.error('Failed to fetch content:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const getContentById = useCallback((id) => {
    return papers.find(p => p.id === id || p.id === `static-${id}`);
  }, [papers]);

  const setCurrentId = useCallback((id) => {
    setCurrentIdState(id);
    const paper = getContentById(id);
    if (paper) {
      setCurrentTags(paper.tags || []);
      setCurrentRelevance(paper.relevant_doctor_specialties || null);
    }
  }, [getContentById]);

  const addContent = useCallback(async (paperData) => {
    try {
      const response = await api.content.create(paperData);
      const newPaper = response.data;
      setPapers(prev => [newPaper, ...prev]);
      return newPaper;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const updateContent = useCallback(async (id, updates) => {
    try {
      const response = await api.content.update(id, updates);
      const updated = response.data;
      setPapers(prev => prev.map(p => p.id === id ? updated : p));
      return updated;
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const deleteContent = useCallback(async (id) => {
    try {
      await api.content.delete(id);
      setPapers(prev => prev.filter(p => p.id !== id));
    } catch (err) {
      setError(err.message);
      throw err;
    }
  }, []);

  const value = {
    papers,
    loading,
    error,
    currentId,
    setCurrentId,
    currentTags,
    setCurrentTags,
    currentRelevance,
    setCurrentRelevance,
    fetchContent,
    getContentById,
    addContent,
    updateContent,
    deleteContent
  };

  return (
    <ContentContext.Provider value={value}>
      {children}
    </ContentContext.Provider>
  );
}
