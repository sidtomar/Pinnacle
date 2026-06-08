import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth';
import styles from './LoginScreen.module.css';

const DEMO_USER = 'admin';
const DEMO_PASS = 'admin';

export default function LoginScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (!username.trim()) { setError('Please enter your username.'); return; }
    if (!password.trim()) { setError('Please enter your password.'); return; }

    if (username.trim().toLowerCase() !== DEMO_USER || password !== DEMO_PASS) {
      setError('Invalid credentials. Use admin / admin for the demo.');
      return;
    }

    setLoading(true);
    await new Promise(r => setTimeout(r, 600));
    login('Admin');
    setLoading(false);
  };

  return (
    <div className={styles.root}>
      <div className={styles.bg} />

      <div className={styles.card}>
        {/* Logo / Brand */}
        <div className={styles.brand}>
          <div className={styles.logoMark}>
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect width="28" height="28" rx="8" fill="#B8912A" />
              <path d="M7 21V10l7-3 7 3v11" stroke="#fff" strokeWidth="2" strokeLinejoin="round" />
              <path d="M11 21v-6h6v6" stroke="#fff" strokeWidth="2" strokeLinejoin="round" />
            </svg>
          </div>
          <div>
            <div className={styles.appName}>PinnacleIQ</div>
            <div className={styles.appTagline}>Medical Intelligence Portal</div>
          </div>
        </div>

        <h1 className={styles.heading}>Welcome back</h1>
        <p className={styles.subheading}>Sign in to your account to continue</p>

        <div className={styles.demoHint}>
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><circle cx="6.5" cy="6.5" r="6" stroke="currentColor" strokeWidth="1.2"/><path d="M6.5 5.5v4M6.5 4h.01" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>
          Demo credentials: <strong>admin</strong> / <strong>admin</strong>
        </div>

        <form className={styles.form} onSubmit={handleSubmit} noValidate>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              className={styles.input}
              placeholder="admin"
              value={username}
              onChange={e => setUsername(e.target.value)}
              autoComplete="username"
              autoFocus
              disabled={loading}
            />
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              className={styles.input}
              placeholder="••••••••"
              value={password}
              onChange={e => setPassword(e.target.value)}
              autoComplete="current-password"
              disabled={loading}
            />
          </div>

          {error && (
            <div className={styles.error}>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <circle cx="7" cy="7" r="6.5" stroke="currentColor" />
                <path d="M7 4v3.5M7 9.5v.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
              {error}
            </div>
          )}

          <button type="submit" className={styles.submitBtn} disabled={loading}>
            {loading ? (
              <>
                <span className={styles.spinner} />
                Signing in…
              </>
            ) : (
              'Sign in'
            )}
          </button>
        </form>

        <p className={styles.footer}>
          © 2026 PinnacleIQ · All rights reserved
        </p>
      </div>
    </div>
  );
}
