import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import styles from '../pages/Dashboard.module.css';

export default function TimelineSection() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const response = await api.sharing.getReport();
        const shareData = response.data || [];

        // Transform share logs into timeline events
        const timelineEvents = shareData.slice(0, 8).map(item => ({
          id: item.id,
          type: 'share',
          title: `Article shared`,
          description: `"${item.title || 'Untitled'}" via ${item.method || 'unknown'}`,
          icon: getIconForMethod(item.method),
          time: formatRelativeTime(item.createdAt || item.date)
        }));

        setEvents(timelineEvents);
      } catch (err) {
        console.error('Failed to fetch timeline:', err);
        setEvents([]);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  const getIconForMethod = (method) => {
    switch (method?.toLowerCase()) {
      case 'whatsapp':
        return '💬';
      case 'email':
        return '📧';
      case 'link':
      case 'copy link':
        return '🔗';
      default:
        return '📤';
    }
  };

  const formatRelativeTime = (dateString) => {
    if (!dateString) return 'Recently';
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffMs = now - date;
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;

      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } catch {
      return 'Recently';
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}></div>
      </div>
    );
  }

  if (!events || events.length === 0) {
    return (
      <div className={styles.emptyState}>
        <div className={styles.emptyIcon}>📅</div>
        <p className={styles.emptyText}>No recent activity</p>
      </div>
    );
  }

  return (
    <div className={styles.timeline}>
      {events.map(event => (
        <div key={event.id} className={styles.timelineItem}>
          <div className={styles.timelineIcon}>{event.icon}</div>
          <div className={styles.timelineContent}>
            <div className={styles.timelineTitle}>{event.title}</div>
            <div className={styles.timelineDesc}>{event.description}</div>
            <div className={styles.timelineTime}>{event.time}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
