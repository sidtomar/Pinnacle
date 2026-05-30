import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';
import MainContent from './MainContent';
import { useAppContext } from '../../hooks/useAppContext';
import styles from './AppLayout.module.css';

export default function AppLayout() {
  const { notifications, removeNotification } = useAppContext();

  return (
    <div className={styles.container}>
      <Sidebar />
      <div className={styles.main}>
        <Header />
        <MainContent />
      </div>
      {/* Toast Notifications */}
      {notifications.length > 0 && (
        <div className={styles.toastContainer}>
          {notifications.map(n => (
            <div key={n.id} className={`${styles.toast} ${styles['toast_' + n.type]}`}>
              <span className={styles.toastIcon}>
                {n.type === 'success' ? '✓' : n.type === 'error' ? '✕' : 'ℹ'}
              </span>
              <span className={styles.toastMsg}>{n.message}</span>
              <button className={styles.toastClose} onClick={() => removeNotification(n.id)}>✕</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
