import React from 'react';
import { useAppContext } from '../../hooks/useAppContext';
import styles from './SortingControls.module.css';

const SORT_OPTIONS = [
  { value: 'date', label: 'Date' },
  { value: 'title', label: 'Title (A-Z)' },
  { value: 'specialty', label: 'Specialty' },
];

export default function SortingControls() {
  const { sortField, sortDirection, setSorting } = useAppContext();

  const handleSortChange = (field) => {
    // If clicking the same field, toggle direction
    if (sortField === field) {
      setSorting(field, sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSorting(field, 'desc');
    }
  };

  return (
    <div className={styles.controls}>
      <span className={styles.label}>Sort by:</span>

      <div className={styles.buttons}>
        {SORT_OPTIONS.map(option => (
          <button
            key={option.value}
            className={`${styles.btn} ${sortField === option.value ? styles.active : ''}`}
            onClick={() => handleSortChange(option.value)}
          >
            {option.label}
            {sortField === option.value && (
              <span className={styles.arrow}>
                {sortDirection === 'asc' ? '↑' : '↓'}
              </span>
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
