import React, { useState } from 'react';
import styles from './ViewToggle.module.css';

export default function ViewToggle({ onViewChange }) {
  const [view, setView] = useState('grid');

  const handleViewChange = (newView) => {
    setView(newView);
    onViewChange(newView);
  };

  return (
    <div className={styles.toggle}>
      <button
        className={`${styles.btn} ${view === 'grid' ? styles.active : ''}`}
        onClick={() => handleViewChange('grid')}
        title="Grid view"
      >
        <svg viewBox="0 0 24 24" fill="currentColor">
          <rect x="3" y="3" width="7" height="7"/>
          <rect x="14" y="3" width="7" height="7"/>
          <rect x="3" y="14" width="7" height="7"/>
          <rect x="14" y="14" width="7" height="7"/>
        </svg>
      </button>
      <button
        className={`${styles.btn} ${view === 'list' ? styles.active : ''}`}
        onClick={() => handleViewChange('list')}
        title="List view"
      >
        <svg viewBox="0 0 24 24" fill="currentColor">
          <line x1="4" y1="6" x2="20" y2="6" strokeWidth="2" stroke="currentColor"/>
          <line x1="4" y1="12" x2="20" y2="12" strokeWidth="2" stroke="currentColor"/>
          <line x1="4" y1="18" x2="20" y2="18" strokeWidth="2" stroke="currentColor"/>
        </svg>
      </button>
    </div>
  );
}
