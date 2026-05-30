import React, { useState, useMemo } from 'react';
import styles from './OccasionHub.module.css';

const OCCASIONS = [
  { id: 1, name: 'World Hypertension Day', date: '2026-05-17', type: 'medical', icon: '🫀',
    desc: 'Raise awareness about hypertension prevention and management with your cardiology panel.',
    doctors: 12, sent: 0, status: 'upcoming' },
  { id: 2, name: 'World Thyroid Day', date: '2026-05-25', type: 'medical', icon: '🦋',
    desc: 'Engage endocrinologists with thyroid awareness campaigns and latest research.',
    doctors: 8, sent: 0, status: 'upcoming' },
  { id: 3, name: 'World No Tobacco Day', date: '2026-05-31', type: 'medical', icon: '🚭',
    desc: 'Share anti-tobacco messaging and lung health papers with your pulmonology network.',
    doctors: 15, sent: 0, status: 'upcoming' },
  { id: 4, name: 'World Environment Day', date: '2026-06-05', type: 'national', icon: '🌍',
    desc: 'Send green greetings and connect environmental health with clinical practice.',
    doctors: 50, sent: 0, status: 'upcoming' },
  { id: 5, name: 'International Yoga Day', date: '2026-06-21', type: 'national', icon: '🧘',
    desc: 'Share holistic health content with doctors interested in lifestyle medicine.',
    doctors: 50, sent: 0, status: 'upcoming' },
  { id: 6, name: 'Doctor\'s Day', date: '2026-07-01', type: 'national', icon: '👨‍⚕️',
    desc: 'Honour your Pinnacle doctors with personalised Doctor\'s Day wishes.',
    doctors: 50, sent: 0, status: 'upcoming' },
  { id: 7, name: 'World Hepatitis Day', date: '2026-07-28', type: 'medical', icon: '🏥',
    desc: 'Engage gastroenterologists and hepatologists with latest hepatitis research.',
    doctors: 6, sent: 0, status: 'upcoming' },
  { id: 8, name: 'Independence Day', date: '2026-08-15', type: 'national', icon: '🇮🇳',
    desc: 'Send patriotic greetings to your entire doctor panel.',
    doctors: 50, sent: 0, status: 'upcoming' },
  { id: 9, name: 'World Heart Day', date: '2026-09-29', type: 'medical', icon: '❤️',
    desc: 'Major engagement opportunity with cardiologists — share heart health papers and campaigns.',
    doctors: 14, sent: 0, status: 'upcoming' },
];

export default function OccasionHub() {
  const [tab, setTab] = useState('upcoming');

  const filtered = useMemo(() => {
    if (tab === 'upcoming') return OCCASIONS.filter(o => o.status === 'upcoming');
    if (tab === 'medical') return OCCASIONS.filter(o => o.type === 'medical');
    if (tab === 'national') return OCCASIONS.filter(o => o.type === 'national' || o.type === 'cultural');
    return OCCASIONS;
  }, [tab]);

  const upcomingThisMonth = OCCASIONS.filter(o => {
    const d = new Date(o.date);
    const now = new Date();
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  }).length;

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
  };

  const daysUntil = (dateStr) => {
    const d = new Date(dateStr);
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    d.setHours(0, 0, 0, 0);
    const diff = Math.ceil((d - now) / (1000 * 60 * 60 * 24));
    if (diff === 0) return 'Today';
    if (diff === 1) return 'Tomorrow';
    if (diff < 0) return 'Passed';
    return `In ${diff} days`;
  };

  const getTypeStyle = (type) => {
    if (type === 'medical') return { bg: 'var(--teal-bg)', color: 'var(--teal)', label: 'Medical Day' };
    if (type === 'national') return { bg: 'var(--amber-bg)', color: 'var(--amber)', label: 'National' };
    return { bg: 'var(--purple-bg)', color: 'var(--purple)', label: 'Cultural' };
  };

  const tabs = [
    { key: 'upcoming', label: 'Upcoming' },
    { key: 'medical', label: 'Medical Days' },
    { key: 'national', label: 'National & Cultural' },
    { key: 'all', label: 'All Occasions' },
  ];

  return (
    <div className={styles.container}>
      {/* Hero Header */}
      <div className={styles.hero}>
        <div className={styles.heroContent}>
          <div>
            <div className={styles.heroLabel}>Broadcast Centre</div>
            <div className={styles.heroTitle}>Occasion Hub</div>
            <div className={styles.heroDesc}>
              Broadcast personalised wishes and campaign messages to Pinnacle doctors on medical, national and cultural occasions.
            </div>
          </div>
          <div className={styles.heroStat}>
            <div className={styles.heroStatValue}>{upcomingThisMonth || 3}</div>
            <div className={styles.heroStatLabel}>Occasions this month</div>
          </div>
        </div>
      </div>

      {/* Filter tabs */}
      <div className={styles.filterRow}>
        <div className={styles.tabGroup}>
          {tabs.map(t => (
            <button
              key={t.key}
              className={`${styles.tab} ${tab === t.key ? styles.tabActive : ''}`}
              onClick={() => setTab(t.key)}
            >
              {t.label}
            </button>
          ))}
        </div>
        <div className={styles.monthLabel}>May–Dec 2026</div>
      </div>

      {/* Occasion cards grid */}
      <div className={styles.grid}>
        {filtered.map(occ => {
          const typeStyle = getTypeStyle(occ.type);
          const remaining = daysUntil(occ.date);
          return (
            <div key={occ.id} className={styles.card}>
              <div className={styles.cardAccent} />
              <div className={styles.cardBody}>
                <div className={styles.cardTop}>
                  <div className={styles.cardIcon}>{occ.icon}</div>
                  <span className={styles.cardTypeBadge} style={{ background: typeStyle.bg, color: typeStyle.color }}>
                    {typeStyle.label}
                  </span>
                </div>
                <div className={styles.cardTitle}>{occ.name}</div>
                <div className={styles.cardDate}>{formatDate(occ.date)} · {remaining}</div>
                <div className={styles.cardDesc}>{occ.desc}</div>
                <div className={styles.cardMeta}>
                  <span className={styles.docCount}>{occ.doctors} doctors eligible</span>
                  {occ.sent > 0 && <span className={styles.sentCount}>{occ.sent} sent</span>}
                </div>
              </div>
              <div className={styles.cardFoot}>
                <button className={styles.broadcastBtn}>Broadcast</button>
                <button className={styles.previewBtn}>Preview</button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
