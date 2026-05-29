import React from 'react';
import ContentCard from './ContentCard';
import styles from './ContentGrid.module.css';

export default function ContentGrid({ data, loading, viewMode = 'grid' }) {
  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.spinner}></div>
        <p>Loading articles...</p>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className={styles.emptyState}>
        <p className={styles.emptyIcon}>📭</p>
        <h3>No articles found</h3>
        <p>Try adjusting your filters or search terms</p>
      </div>
    );
  }

  return (
    <div className={viewMode === 'list' ? styles.listView : styles.gridView}>
      {data.map(item => (
        <ContentCard key={item.id || item._id} item={item} />
      ))}
    </div>
  );
}
