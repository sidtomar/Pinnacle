import React from 'react';
import styles from './Placeholder.module.css';

export default function Placeholder({ page, role }) {
  return (
    <div className={styles.placeholder}>
      <div className={styles.content}>
        <h1>🚀 {page.charAt(0).toUpperCase() + page.slice(1)} Page</h1>
        <p>This page is coming soon!</p>
        <p className={styles.meta}>
          Role: <strong>{role}</strong> | Page: <strong>{page}</strong>
        </p>
      </div>
    </div>
  );
}
