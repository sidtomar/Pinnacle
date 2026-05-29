import React, { useState } from 'react';
import styles from './ContentCard.module.css';
import ShareDialog from '../dialogs/ShareDialog';

export default function ContentCard({ item }) {
  const [showShareDialog, setShowShareDialog] = useState(false);

  const getStatusClass = (status) => {
    if (status === 'approved') return styles.statusApproved;
    if (status === 'pending') return styles.statusPending;
    if (status === 'rejected') return styles.statusRejected;
    return '';
  };

  const status = item.status || 'approved';
  const title = item.title || 'Untitled';
  const authors = item.authors || 'NA';
  const summary = item.summary || item.whatsapp_summary || '';
  const tags = item.tags || [];
  const pmid = item.pmid || 'NA';
  const doi = item.doi || 'NA';
  const pubmedLink = item.pubmed_link || '';
  const fullTextLink = item.full_text_link || '';
  const publishDate = item.publication_date || item.created_at?.split('T')[0] || 'NA';

  return (
    <>
      <div className={`${styles.card} ${getStatusClass(status)}`}>
        <div className={styles.accent}></div>

        <div className={styles.body}>
          <h3 className={styles.title}>{title}</h3>

          <p className={styles.authors}>{authors}</p>

          {summary && <p className={styles.summary}>{summary}</p>}

          {tags.length > 0 && (
            <div className={styles.tags}>
              {tags.slice(0, 3).map((tag, idx) => (
                <span key={idx} className={styles.tag}>{tag}</span>
              ))}
              {tags.length > 3 && <span className={styles.tagMore}>+{tags.length - 3}</span>}
            </div>
          )}

          <div className={styles.pubDetails}>
            <div className={styles.pubHeader}>PUBLICATION DETAILS</div>

            <div className={styles.pubRow}>
              <div className={styles.pubLabel}>PMID</div>
              <div className={styles.pubValue}>{pmid}</div>
            </div>

            <div className={styles.pubRow}>
              <div className={styles.pubLabel}>DOI</div>
              <div className={styles.pubValue}>{doi}</div>
            </div>

            <div className={styles.pubRow}>
              <div className={styles.pubLabel}>Date</div>
              <div className={styles.pubValue}>{publishDate}</div>
            </div>

            {pubmedLink && (
              <a href={pubmedLink} target="_blank" rel="noopener noreferrer" className={styles.link}>
                📄 PubMed Link
              </a>
            )}

            {fullTextLink && (
              <a href={fullTextLink} target="_blank" rel="noopener noreferrer" className={styles.link}>
                📑 Full Text (DOI)
              </a>
            )}
          </div>
        </div>

        <div className={styles.footer}>
          <button className={styles.shareBtn} onClick={() => setShowShareDialog(true)}>
            Share
          </button>
        </div>
      </div>

      {showShareDialog && (
        <ShareDialog item={item} onClose={() => setShowShareDialog(false)} />
      )}
    </>
  );
}
