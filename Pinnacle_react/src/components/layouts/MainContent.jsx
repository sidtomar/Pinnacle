import React from 'react';
import { useRouter } from '../../hooks/useRouter';
import { useAuth } from '../../hooks/useAuth';
import styles from './MainContent.module.css';

// Page components
import ContentLibrary from '../pages/ContentLibrary';
import TodaysTasks from '../pages/TodaysTasks';
import DoctorDirectory from '../pages/DoctorDirectory';
import Doctor360 from '../pages/Doctor360';
import OccasionHub from '../pages/OccasionHub';
import Analytics from '../pages/Analytics';
import Pipeline from '../pages/Pipeline';
import Dashboard from '../pages/Dashboard';
import Placeholder from '../pages/Placeholder';

const PAGE_COMPONENTS = {
  'library': ContentLibrary,
  'today': TodaysTasks,
  'doctors': DoctorDirectory,
  'doctor360': Doctor360,
  'occasions': OccasionHub,
  'analytics': Analytics,
  'pipeline': Pipeline,
  'dashboard': Dashboard,
};

export default function MainContent() {
  const { currentPage } = useRouter();
  const { role } = useAuth();

  const PageComponent = PAGE_COMPONENTS[currentPage] || Placeholder;

  return (
    <div className={styles.contentArea}>
      <PageComponent role={role} page={currentPage} />
    </div>
  );
}
