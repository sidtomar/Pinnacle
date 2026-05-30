import React from 'react';
import styles from './KpiCard.module.css';

export default function KpiCard({ label, value, icon, trend, color = 'blue' }) {
  return (
    <div className={`${styles.card} ${styles[color]}`}>
      <div className={styles.header}>
        <div className={styles.labelWrapper}>
          <p className={styles.label}>{label}</p>
          {trend && (
            <span className={`${styles.trend} ${trend.direction === 'up' ? styles.up : styles.down}`}>
              {trend.direction === 'up' ? '↑' : '↓'} {trend.value}%
            </span>
          )}
        </div>
        <div className={styles.icon}>{icon}</div>
      </div>
      <p className={styles.value}>{value}</p>
    </div>
  );
}
