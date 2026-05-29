import React, { useState, useEffect } from 'react';
import { useAppContext } from '../../hooks/useAppContext';
import styles from './SearchBar.module.css';

export default function SearchBar() {
  const [input, setInput] = useState('');
  const { filters, setFilters } = useAppContext();

  // Debounce search (300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters({ search: input });
    }, 300);

    return () => clearTimeout(timer);
  }, [input, setFilters]);

  const handleClear = () => {
    setInput('');
    setFilters({ search: '' });
  };

  return (
    <div className={styles.searchBox}>
      <svg className={styles.icon} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="8"></circle>
        <path d="m21 21-4.35-4.35"></path>
      </svg>
      <input
        type="text"
        placeholder="Search articles by title, authors, or keywords..."
        value={input}
        onChange={(e) => setInput(e.target.value)}
        className={styles.input}
      />
      {input && (
        <button className={styles.clearBtn} onClick={handleClear} title="Clear search">
          ✕
        </button>
      )}
    </div>
  );
}
