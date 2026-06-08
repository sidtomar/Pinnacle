import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useAppContext } from '../../hooks/useAppContext';
import { useRouter } from '../../hooks/useRouter';
import styles from './Header.module.css';

const SAMPLE_NOTIFICATIONS = [
  { id: 'n1', type: 'new', icon: '📄', title: 'New paper added to Library', msg: 'SGLT2 Meta-Analysis auto-fetched from PubMed and pending review.', time: '5 min ago', unread: true },
  { id: 'n2', type: 'approved', icon: '✅', title: 'Content approved', msg: 'Inositol vs Metformin in PCOS approved by Dr. Prashant Agarwal.', time: '1 hr ago', unread: true },
  { id: 'n3', type: 'improvement', icon: '📈', title: 'DMS improvement alert', msg: 'Dr. Jayesh Shah\'s engagement score increased by 12 points this week.', time: '3 hr ago', unread: false },
];

const PAGE_LABELS = {
  library: 'Content Library',
  today: "Today's Tasks",
  doctors: 'Doctor Directory',
  doctor360: 'Doctor 360°',
  occasions: 'Occasion Hub',
  analytics: 'Analytics',
  pipeline: 'Research Pipeline',
  dashboard: 'Dashboard',
};

/* Maps notification type → destination page for navigation */
const NOTIF_DESTINATION = {
  new:         { page: 'library', label: 'Content Library' },
  approved:    { page: 'library', label: 'Content Library' },
  improvement: { page: 'doctors', label: 'Doctor Directory' },
};

export default function Header() {
  const { role, setRole, isMA, user, logout } = useAuth();
  const { currentPage, navigateTo } = useRouter();
  const { toggleSidebar } = useAppContext();
  const [isRoleDropdownOpen, setIsRoleDropdownOpen] = useState(false);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userMenuRef = useRef(null);
  const [notifications, setNotifications] = useState(SAMPLE_NOTIFICATIONS);
  const dropdownRef = useRef(null);
  const notifRef = useRef(null);

  const unreadCount = notifications.filter(n => n.unread).length;

  /* FB-001: Click notification → mark read + navigate to relevant screen */
  const handleNotifClick = (n) => {
    // Mark this notification as read
    setNotifications(prev => prev.map(x => x.id === n.id ? { ...x, unread: false } : x));
    // Close bell dropdown
    setIsNotifOpen(false);
    // Navigate to the associated screen
    const dest = NOTIF_DESTINATION[n.type] || { page: 'library' };
    navigateTo(dest.page);
  };

  /* FB-002: Mark all read — clears badge */
  const markAllRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, unread: false })));
  };

  const handleRoleChange = (newRole) => {
    setRole(newRole);
    setIsRoleDropdownOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsRoleDropdownOpen(false);
      }
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setIsNotifOpen(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(e.target)) {
        setIsUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className={styles.header}>
      {/* Hamburger — only visible on tablet/mobile */}
      <button className={styles.hamburger} onClick={toggleSidebar} aria-label="Open menu">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          <line x1="3" y1="5" x2="17" y2="5"/>
          <line x1="3" y1="10" x2="17" y2="10"/>
          <line x1="3" y1="15" x2="17" y2="15"/>
        </svg>
      </button>

      <div className={styles.breadcrumb}>
        <span className={styles.breadcrumbBase}>PinnacleIQ</span>
        <span className={styles.separator}>›</span>
        <span className={styles.currentPage}>{PAGE_LABELS[currentPage] || 'PinnacleIQ'}</span>
      </div>

      <div className={styles.rightSection}>
        {/* Role Switcher */}
        <div
          className={`${styles.roleSwitcher} ${isRoleDropdownOpen ? styles.open : ''} ${isMA ? styles.roleMa : ''}`}
          ref={dropdownRef}
        >
          <button
            className={styles.roleSwitcherBtn}
            onClick={() => setIsRoleDropdownOpen(!isRoleDropdownOpen)}
          >
            <div>
              <div className={styles.roleLabel}>Viewing as</div>
              <div className={styles.roleValue}>
                {isMA ? 'Dr. Prashant Agarwal · MA' : 'Jijo · PMT'}
              </div>
            </div>
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" className={styles.arrow}>
              <polyline points="3,5 7,9 11,5"/>
            </svg>
          </button>

          {isRoleDropdownOpen && (
            <div className={styles.roleDropdown} onClick={e => e.stopPropagation()}>
              <div className={styles.dropdownHeading}>Switch Role</div>
              <button
                className={`${styles.roleOption} ${role === 'bu-head' ? styles.selected : ''}`}
                onClick={() => handleRoleChange('bu-head')}
              >
                <div className={`${styles.roleAvatar} ${styles.roleAvatarPMT}`}>J</div>
                <div className={styles.roleOptionInfo}>
                  <div className={styles.roleOptionName}>Jijo</div>
                  <div className={styles.roleOptionDesc}>BU Head · PMT · Life Division</div>
                </div>
                {role === 'bu-head' && <span className={styles.check}>✓</span>}
              </button>
              <div className={styles.dropdownDivider} />
              <button
                className={`${styles.roleOption} ${role === 'medical-affairs' ? styles.selected : ''}`}
                onClick={() => handleRoleChange('medical-affairs')}
              >
                <div className={`${styles.roleAvatar} ${styles.roleAvatarMA}`}>PA</div>
                <div className={styles.roleOptionInfo}>
                  <div className={styles.roleOptionName}>Dr. Prashant Agarwal</div>
                  <div className={styles.roleOptionDesc}>Medical Affairs · MA</div>
                </div>
                {role === 'medical-affairs' && <span className={styles.check}>✓</span>}
              </button>
            </div>
          )}
        </div>

        {/* Notification Bell */}
        <div className={styles.notifBell} ref={notifRef}>
          <button
            className={styles.notifBellBtn}
            onClick={() => setIsNotifOpen(prev => !prev)}
            title="Notifications"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
              <path d="M8 1.5a5.5 5.5 0 015.5 5.5v2.5l1 2H1.5l1-2V7A5.5 5.5 0 018 1.5z"/>
              <path d="M6.5 13.5a1.5 1.5 0 003 0"/>
            </svg>
            {unreadCount > 0 && (
              <span className={styles.notifBadge}>{unreadCount}</span>
            )}
          </button>

          {isNotifOpen && (
            <div className={styles.notifDropdown} onClick={e => e.stopPropagation()}>
              <div className={styles.notifHeader}>
                <div className={styles.notifHeaderTitle}>Notifications</div>
                {unreadCount > 0 && (
                  <button className={styles.notifMarkAll} onClick={markAllRead}>Mark all read</button>
                )}
              </div>
              <div className={styles.notifList}>
                {notifications.length === 0 ? (
                  <div className={styles.notifEmpty}>No notifications yet</div>
                ) : (
                  notifications.map(n => {
                    const dest = NOTIF_DESTINATION[n.type] || { label: 'View' };
                    const iconClass = n.type === 'new'
                      ? styles.notifIconNew
                      : n.type === 'approved'
                      ? styles.notifIconApproved
                      : styles.notifIconImprovement;
                    return (
                      <div
                        key={n.id}
                        className={`${styles.notifItem} ${n.unread ? styles.notifUnread : ''}`}
                        onClick={() => handleNotifClick(n)}
                        title={`Go to ${dest.label}`}
                      >
                        <div className={`${styles.notifIcon} ${iconClass}`}>
                          {n.icon}
                        </div>
                        <div className={styles.notifBody}>
                          <div className={styles.notifTitle}>{n.title}</div>
                          <div className={styles.notifMsg}>{n.msg}</div>
                          <div className={styles.notifMeta}>
                            <span className={styles.notifTime}>{n.time}</span>
                            <span className={styles.notifNav}>→ {dest.label}</span>
                          </div>
                        </div>
                        {n.unread && <div className={styles.notifDot} />}
                      </div>
                    );
                  })
                )}
              </div>
            </div>
          )}
        </div>

        {/* MA: Add Content button */}
        {isMA && currentPage === 'library' && (
          <button className={styles.addContentBtn}>+ Add Content</button>
        )}

        {/* User avatar + logout */}
        <div className={styles.userMenu} ref={userMenuRef}>
          <button
            className={styles.userAvatar}
            onClick={() => setIsUserMenuOpen(prev => !prev)}
            title={user || 'Account'}
          >
            {user ? user[0].toUpperCase() : 'U'}
          </button>
          {isUserMenuOpen && (
            <div className={styles.userDropdown} onClick={e => e.stopPropagation()}>
              <div className={styles.userDropdownEmail}>{user}</div>
              <div className={styles.userDropdownDivider} />
              <button className={styles.logoutBtn} onClick={logout}>
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
                  <path d="M5 2H2a1 1 0 00-1 1v7a1 1 0 001 1h3M9 9.5l2.5-3L9 3M11.5 6.5H5"/>
                </svg>
                Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
