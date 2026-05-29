import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useAppContext } from '../../hooks/useAppContext';
import { useRouter } from '../../hooks/useRouter';
import styles from './Header.module.css';

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

export default function Header() {
  const { role, setRole, isMA } = useAuth();
  const { currentPage } = useRouter();
  const { toggleSidebar } = useAppContext();
  const [isRoleDropdownOpen, setIsRoleDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  const handleRoleChange = (newRole) => {
    setRole(newRole);
    setIsRoleDropdownOpen(false);
  };

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsRoleDropdownOpen(false);
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
        {/* MA: Add Content button */}
        {isMA && currentPage === 'library' && (
          <button className={styles.addContentBtn}>+ Add Content</button>
        )}

        {/* Role Switcher */}
        <div
          className={`${styles.roleSwitcher} ${isRoleDropdownOpen ? styles.open : ''} ${isMA ? styles.roleMa : ''}`}
          ref={dropdownRef}
          data-initials={isMA ? 'PA' : 'J'}
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
      </div>
    </header>
  );
}
