import React, { useState, useMemo } from 'react';
import { useContent } from '../../hooks/useContent';
import { useAppContext } from '../../hooks/useAppContext';
import styles from './FilterPanel.module.css';

export default function FilterPanel() {
  const { papers } = useContent();
  const { filters, setFilters, clearFilters } = useAppContext();
  const [isOpen, setIsOpen] = useState(true);

  // Extract unique values from papers
  const specialties = useMemo(() =>
    [...new Set(papers.map(p => p.specialty).filter(Boolean))].sort(),
    [papers]
  );

  const therapyAreas = useMemo(() =>
    [...new Set(papers.map(p => p.therapy_area).filter(Boolean))].sort(),
    [papers]
  );

  const allTags = useMemo(() => {
    const tags = new Set();
    papers.forEach(p => {
      const paperTags = p.tags || [];
      if (Array.isArray(paperTags)) {
        paperTags.forEach(t => tags.add(t));
      }
    });
    return [...tags].sort();
  }, [papers]);

  const toggleSpecialty = (specialty) => {
    const updated = filters.specialty.includes(specialty)
      ? filters.specialty.filter(s => s !== specialty)
      : [...filters.specialty, specialty];
    setFilters({ specialty: updated });
  };

  const toggleTherapyArea = (area) => {
    const updated = filters.therapyArea.includes(area)
      ? filters.therapyArea.filter(a => a !== area)
      : [...filters.therapyArea, area];
    setFilters({ therapyArea: updated });
  };

  const toggleTag = (tag) => {
    const updated = filters.tags.includes(tag)
      ? filters.tags.filter(t => t !== tag)
      : [...filters.tags, tag];
    setFilters({ tags: updated });
  };

  const hasActiveFilters = filters.specialty.length > 0 ||
    filters.therapyArea.length > 0 ||
    filters.tags.length > 0 ||
    filters.dateRange.start ||
    filters.dateRange.end;

  return (
    <div className={styles.filterPanel}>
      <div className={styles.header}>
        <h3 className={styles.title}>Filters</h3>
        {hasActiveFilters && (
          <button className={styles.clearBtn} onClick={clearFilters}>
            Clear All
          </button>
        )}
        <button
          className={styles.toggleBtn}
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? '▼' : '▶'}
        </button>
      </div>

      {isOpen && (
        <div className={styles.content}>
          {/* Specialty Filter */}
          <div className={styles.filterGroup}>
            <h4 className={styles.groupTitle}>Specialty</h4>
            <div className={styles.options}>
              {specialties.length === 0 ? (
                <p className={styles.empty}>No specialties</p>
              ) : (
                specialties.map(specialty => (
                  <label key={specialty} className={styles.option}>
                    <input
                      type="checkbox"
                      checked={filters.specialty.includes(specialty)}
                      onChange={() => toggleSpecialty(specialty)}
                      className={styles.checkbox}
                    />
                    <span className={styles.label}>{specialty}</span>
                  </label>
                ))
              )}
            </div>
          </div>

          {/* Therapy Area Filter */}
          <div className={styles.filterGroup}>
            <h4 className={styles.groupTitle}>Therapy Area</h4>
            <div className={styles.options}>
              {therapyAreas.length === 0 ? (
                <p className={styles.empty}>No therapy areas</p>
              ) : (
                therapyAreas.map(area => (
                  <label key={area} className={styles.option}>
                    <input
                      type="checkbox"
                      checked={filters.therapyArea.includes(area)}
                      onChange={() => toggleTherapyArea(area)}
                      className={styles.checkbox}
                    />
                    <span className={styles.label}>{area}</span>
                  </label>
                ))
              )}
            </div>
          </div>

          {/* Tags Filter */}
          {allTags.length > 0 && (
            <div className={styles.filterGroup}>
              <h4 className={styles.groupTitle}>Tags</h4>
              <div className={styles.tagsContainer}>
                {allTags.slice(0, 15).map(tag => (
                  <button
                    key={tag}
                    className={`${styles.tag} ${filters.tags.includes(tag) ? styles.tagActive : ''}`}
                    onClick={() => toggleTag(tag)}
                  >
                    {tag}
                    {filters.tags.includes(tag) && <span className={styles.tagX}>✕</span>}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Active Filter Badges */}
          {hasActiveFilters && (
            <div className={styles.activeBadges}>
              {filters.specialty.map(s => (
                <span key={`spec-${s}`} className={styles.badge}>
                  {s} <button onClick={() => toggleSpecialty(s)} className={styles.badgeX}>✕</button>
                </span>
              ))}
              {filters.therapyArea.map(a => (
                <span key={`area-${a}`} className={styles.badge}>
                  {a} <button onClick={() => toggleTherapyArea(a)} className={styles.badgeX}>✕</button>
                </span>
              ))}
              {filters.tags.map(t => (
                <span key={`tag-${t}`} className={styles.badge}>
                  {t} <button onClick={() => toggleTag(t)} className={styles.badgeX}>✕</button>
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
