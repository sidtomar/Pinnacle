import React from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useAppContext } from '../../hooks/useAppContext';
import { useRouter } from '../../hooks/useRouter';
import styles from './Sidebar.module.css';

/**
 * Navigation config per role.
 * Research Pipeline = admin/debug only — NOT shown to any end-user persona.
 * MA sees only: Content Library (+ Access Level panel rendered separately).
 * PMT sees all 7 BRD modules: Today's Tasks, Content Library, Doctor Directory,
 *   Doctor 360°, Occasion Hub, Analytics, Dashboard.
 */
const NAV_ITEMS = {
  'admin': {
    main: { label: 'Admin Tools', items: [
      { id: 'pipeline',        label: 'Research Agent',  icon: '🔬' },
      { id: 'admin-pipeline',  label: 'Admin Pipeline',  icon: '⚙️' },
    ]}
  },
  'medical-affairs': {
    main: { label: 'My Workspace', items: [
      { id: 'library', label: 'Content Library', icon: '📄', badgeKey: 'pending' },
    ]}
  },
  'bu-head': {
    main: { label: 'Modules', items: [
      { id: 'today',     label: "Today's Tasks",   icon: '🕐', badge: '9' },
      { id: 'library',   label: 'Content Library',  icon: '📄' },
      { id: 'doctors',   label: 'Doctor Directory', icon: '👤' },
      { id: 'doctor360', label: 'Doctor 360°',      icon: '🎯' },
      { id: 'occasions', label: 'Occasion Hub',     icon: '⭐' },
      { id: 'analytics', label: 'Analytics',        icon: '📈' },
      { id: 'dashboard', label: 'Dashboard',        icon: '📊' },
    ]},
  }
};

// Demo pending count — in production this comes from ContentContext/API
const MA_PENDING_COUNT = 2;

export default function Sidebar() {
  const { role, isAdmin, isMA, user } = useAuth();
  const { currentTab, setCurrentTab, sidebarOpen, toggleSidebar } = useAppContext();
  const { navigate } = useRouter();
  const navGroups = NAV_ITEMS[role] || {};

  const handleNavClick = (pageId) => {
    setCurrentTab(pageId);
    navigate(role, pageId);
    if (sidebarOpen) toggleSidebar();
  };

  /* Resolve badge value — static badge or dynamic badgeKey */
  const getBadge = (item) => {
    if (item.badge) return item.badge;
    if (item.badgeKey === 'pending' && isMA) return MA_PENDING_COUNT > 0 ? String(MA_PENDING_COUNT) : null;
    return null;
  };

  const renderNavGroup = (group) => (
    <div className={styles.navGroup}>
      {group.items.map(item => {
        const badge = getBadge(item);
        return (
          <button
            key={item.id}
            className={`${styles.navItem} ${currentTab === item.id ? (isAdmin ? styles.activeAdmin : isMA ? styles.activeMA : styles.activePMT) : ''}`}
            onClick={() => handleNavClick(item.id)}
          >
            <span className={styles.navIcon}>{item.icon}</span>
            <span className={styles.navLabel}>{item.label}</span>
            {badge && (
              <span className={`${styles.navBadge} ${isAdmin ? styles.badgeAdmin : isMA ? styles.badgeAmber : styles.badgeGold}`}>
                {badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );

  return (
    <>
      {/* Mobile backdrop */}
      <div
        className={`${styles.backdrop} ${sidebarOpen ? styles.backdropOpen : ''}`}
        onClick={toggleSidebar}
      />

      <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ''}`}>
        <div className={styles.logo}>
          <div className={styles.logoWm}>Mankind Pharma</div>
          <div className={styles.logoTitle}>
            Pinnacle<span>IQ</span>
          </div>
          <div className={styles.logoSub}>Doctor Intelligence Platform</div>
        </div>

        <div className={styles.user}>
          <div className={`${styles.avatar} ${isAdmin ? styles.avatarAdmin : isMA ? styles.avatarMA : styles.avatarPMT}`}>
            {isAdmin ? 'A' : isMA ? 'PA' : 'J'}
          </div>
          <div className={styles.userInfo}>
            <div className={styles.userName}>
              {isAdmin ? (user || 'Admin') : isMA ? 'Dr. Prashant Agarwal' : 'Jijo'}
            </div>
            <div className={styles.userRole}>
              {isAdmin ? 'Administrator' : isMA ? 'Medical Affairs' : 'BU Head · PMT'}
            </div>
          </div>
          <div className={`${styles.roleBadge} ${isAdmin ? styles.badgeAdmin : isMA ? styles.badgeMA : styles.badgePMT}`}>
            {isAdmin ? 'ADMIN' : isMA ? 'MA' : 'PMT'}
          </div>
        </div>

        <nav className={styles.nav}>
          {/* Main nav group */}
          {navGroups.main && (
            <>
              <div className={styles.navGroupLabel}>{navGroups.main.label}</div>
              {renderNavGroup(navGroups.main)}
            </>
          )}

          {/* Admin: access info panel */}
          {isAdmin && (
            <>
              <div className={styles.navGroupLabel} style={{ marginTop: 8 }}>Access Level</div>
              <div className={styles.accessPanel}>
                <div className={styles.accessTitle}>Permissions</div>
                <div className={styles.accessList}>
                  {['Run Research Agent', 'Run Admin Pipeline', 'Generate Articles', 'View All Roles'].map(p => (
                    <div key={p} className={styles.accessItem}>
                      <span className={styles.accessDotGreen}>✓</span>{p}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}

          {/* MA: Access Level panel */}
          {isMA && (
            <>
              <div className={styles.navGroupLabel} style={{ marginTop: 8 }}>Access Level</div>
              <div className={styles.accessPanel}>
                <div className={styles.accessTitle}>Permissions</div>
                <div className={styles.accessList}>
                  {['Review & Approve', 'Edit Summaries & Tags', 'Upload / Add Content'].map(p => (
                    <div key={p} className={styles.accessItem}>
                      <span className={styles.accessDotGreen}>✓</span>{p}
                    </div>
                  ))}
                  {['Doctor Engagement', 'Send to Doctors'].map(p => (
                    <div key={p} className={styles.accessItemDisabled}>
                      <span className={styles.accessDotGray}>✕</span>{p}
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </nav>

        <div className={styles.footer}>
          {!isMA ? (
            <>
              <div className={styles.stats}>
                <div className={styles.stat}>
                  <div className={styles.statValue}>50</div>
                  <div className={styles.statLabel}>Doctors</div>
                </div>
                <div className={styles.stat}>
                  <div className={styles.statValue}>74%</div>
                  <div className={styles.statLabel}>Coverage</div>
                </div>
              </div>
              <div className={styles.syncRow}>
                <div className={styles.syncDot}></div>
                PubMed sync · 14 min ago
              </div>
            </>
          ) : (
            <>
              <div className={styles.syncRow}>
                <div className={styles.syncDot}></div>
                PubMed sync · 14 min ago · 3 new
              </div>
              <div className={styles.syncSub}>Last review: Today 11:30 AM</div>
            </>
          )}
        </div>
      </aside>
    </>
  );
}
