import React, { useState } from 'react';
import Modal from '../shared/Modal';
import { api } from '../../services/api';
import { useAppContext } from '../../hooks/useAppContext';
import styles from './ShareDialog.module.css';

export default function ShareDialog({ item, onClose }) {
  const [method, setMethod] = useState('whatsapp');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const { addNotification } = useAppContext();

  const handleShare = async () => {
    setLoading(true);
    try {
      const contentId = item.id || item._id;
      await api.sharing.logShare(contentId, method);
      addNotification(`✓ Shared via ${method}`, 'success');
      onClose();
    } catch (error) {
      addNotification(`✗ Failed to log share: ${error.message}`, 'error', 5000);
    } finally {
      setLoading(false);
    }
  };

  const shareMessage = item.whatsapp_summary || item.summary || item.title || 'Check out this article';

  const shareOptions = [
    {
      id: 'whatsapp',
      label: 'WhatsApp',
      icon: '💬',
      description: 'Share on WhatsApp'
    },
    {
      id: 'email',
      label: 'Email',
      icon: '📧',
      description: 'Send via email'
    },
    {
      id: 'link',
      label: 'Copy Link',
      icon: '🔗',
      description: 'Copy link to clipboard'
    }
  ];

  return (
    <Modal isOpen={true} onClose={onClose} title="Share Article">
      <div className={styles.container}>
        <div className={styles.preview}>
          <h3 className={styles.previewTitle}>{item.title}</h3>
          {item.whatsapp_summary && (
            <p className={styles.previewText}>{item.whatsapp_summary}</p>
          )}
          {item.pubmed_link && (
            <p className={styles.previewLink}>
              <span className={styles.linkIcon}>🔗</span>
              {item.pubmed_link}
            </p>
          )}
        </div>

        <div className={styles.options}>
          <label className={styles.label}>Choose sharing method:</label>
          <div className={styles.optionsGrid}>
            {shareOptions.map(option => (
              <button
                key={option.id}
                className={`${styles.option} ${method === option.id ? styles.selected : ''}`}
                onClick={() => setMethod(option.id)}
              >
                <span className={styles.icon}>{option.icon}</span>
                <span className={styles.name}>{option.label}</span>
                <span className={styles.desc}>{option.description}</span>
              </button>
            ))}
          </div>
        </div>

        {message && (
          <div className={styles.messageBox}>
            <p className={styles.messageLabel}>Message Preview:</p>
            <p className={styles.messageText}>{message}</p>
          </div>
        )}

        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button
            className={styles.shareBtn}
            onClick={handleShare}
            disabled={loading}
          >
            {loading ? 'Sharing...' : 'Share Now'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
