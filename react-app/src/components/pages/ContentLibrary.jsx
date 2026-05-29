import React, { useState } from 'react';
import { useContent } from '../../hooks/useContent';
import { useAppContext } from '../../hooks/useAppContext';
import { useFilters } from '../../hooks/useFilters';
import SearchBar from '../shared/SearchBar';
import FilterPanel from '../shared/FilterPanel';
import SortingControls from '../shared/SortingControls';
import ViewToggle from '../shared/ViewToggle';
import ContentGrid from '../shared/ContentGrid';
import styles from './ContentLibrary.module.css';

export default function ContentLibrary() {
  const { papers, loading } = useContent();
  const { filters, sortField, sortDirection } = useAppContext();
  const { filteredData } = useFilters(papers, filters);
  const [viewMode, setViewMode] = useState('grid');

  return (
    <div className={styles.container}>
      {/* Header Section */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Content Library</h1>
          <p className={styles.subtitle}>
            {loading ? 'Loading...' : `${filteredData.length} of ${papers.length} articles`}
          </p>
        </div>
      </div>

      {/* Search & Controls Bar */}
      <div className={styles.controlsBar}>
        <SearchBar />
        <div className={styles.rightControls}>
          <ViewToggle onViewChange={setViewMode} />
        </div>
      </div>

      {/* Main Content Area */}
      <div className={styles.content}>
        {/* Sidebar: Filter Panel */}
        <aside className={styles.sidebar}>
          <FilterPanel />
        </aside>

        {/* Main: Grid/List */}
        <main className={styles.main}>
          <SortingControls />
          <ContentGrid
            data={filteredData}
            loading={loading}
            viewMode={viewMode}
          />
        </main>
      </div>
    </div>
  );
}
