import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import styles from '../pages/Dashboard.module.css';

export default function SharingReportTable() {
  const [shareData, setShareData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchReport = async () => {
      try {
        setLoading(true);
        const response = await api.sharing.getReport();
        setShareData(response.data || []);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch sharing report:', err);
        setError(err.message);
        setShareData([]);
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, []);

  const getMethodBadgeColor = (method) => {
    switch (method?.toLowerCase()) {
      case 'whatsapp':
        return styles.methodWhatsapp;
      case 'email':
        return styles.methodEmail;
      case 'link':
      case 'copy link':
        return styles.methodLink;
      default:
        return styles.methodLink;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
        <span>Loading sharing report...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyIcon}>⚠️</div>
        <p className={styles.emptyText}>Failed to load sharing report</p>
      </div>
    );
  }

  if (!shareData || shareData.length === 0) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyIcon}>📊</div>
        <p className={styles.emptyText}>No sharing activity yet</p>
      </div>
    );
  }

  return (
    <div className={styles.tableWrapper}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th>Article Title</th>
            <th>Method</th>
            <th>Date</th>
            <th>User</th>
          </tr>
        </thead>
        <tbody>
          {shareData.map((item, idx) => (
            <tr key={item.id || idx}>
              <td title={item.title}>{item.title || 'Untitled'}</td>
              <td>
                <span className={`${styles.methodBadge} ${getMethodBadgeColor(item.method)}`}>
                  {item.method || 'Unknown'}
                </span>
              </td>
              <td>{formatDate(item.createdAt || item.date)}</td>
              <td>{item.user || item.userId || 'Anonymous'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
