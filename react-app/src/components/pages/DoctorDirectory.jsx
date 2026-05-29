import React, { useState, useEffect, useMemo } from 'react';
import { api } from '../../services/api';
import { useAppContext } from '../../hooks/useAppContext';
import { useRouter } from '../../hooks/useRouter';
import styles from './DoctorDirectory.module.css';

const STATIC_DOCTORS = [
  { id: 1, name: 'Dr. Priya Sharma',   specialty: 'Gynaecology', city: 'Mumbai',    category: 'A+', dm_score: 85, sow: 42, score: 78, status: 'high', last_engaged: '2026-05-25', next_action: 'Share PCOS article',       action_type: 'content' },
  { id: 2, name: 'Dr. Rajesh Patel',   specialty: 'Cardiology',  city: 'Delhi',     category: 'A+', dm_score: 92, sow: 55, score: 88, status: 'high', last_engaged: '2026-05-27', next_action: 'Invite to webinar',        action_type: 'event' },
  { id: 3, name: 'Dr. Anjali Desai',   specialty: 'Paediatrics', city: 'Bangalore', category: 'A',  dm_score: 71, sow: 33, score: 62, status: 'med',  last_engaged: '2026-05-18', next_action: 'Share vaccination update', action_type: 'content' },
  { id: 4, name: 'Dr. Vikram Singh',   specialty: 'Oncology',    city: 'Chennai',   category: 'A+', dm_score: 88, sow: 48, score: 82, status: 'high', last_engaged: '2026-05-22', next_action: 'Schedule clinic visit',    action_type: 'event' },
  { id: 5, name: 'Dr. Meera Krishnan', specialty: 'Dermatology', city: 'Hyderabad', category: 'A',  dm_score: 65, sow: 28, score: 55, status: 'med',  last_engaged: '2026-05-10', next_action: 'Share acne study',         action_type: 'content' },
  { id: 6, name: 'Dr. Arun Gupta',     specialty: 'Cardiology',  city: 'Kolkata',   category: 'A',  dm_score: 58, sow: 22, score: 45, status: 'low',  last_engaged: '2026-04-15', next_action: 'Re-engage with content',  action_type: 'overdue' },
  { id: 7, name: 'Dr. Sunita Reddy',   specialty: 'Neurology',   city: 'Pune',      category: 'A+', dm_score: 90, sow: 52, score: 85, status: 'high', last_engaged: '2026-05-26', next_action: 'Follow up on feedback',   action_type: 'content' },
  { id: 8, name: 'Dr. Karan Mehta',    specialty: 'Gynaecology', city: 'Ahmedabad', category: 'A',  dm_score: 72, sow: 35, score: 63, status: 'med',  last_engaged: '2026-05-14', next_action: 'Share GLP-1 article',     action_type: 'content' },
  { id: 9, name: 'Dr. Nisha Joshi',    specialty: 'Paediatrics', city: 'Mumbai',    category: 'A+', dm_score: 80, sow: 41, score: 74, status: 'high', last_engaged: '2026-05-20', next_action: 'Invite to CME event',     action_type: 'event' },
  { id: 10, name: 'Dr. Rahul Verma',   specialty: 'Cardiology',  city: 'Delhi',     category: 'A',  dm_score: 50, sow: 18, score: 38, status: 'low',  last_engaged: '2026-04-02', next_action: 'Urgent re-engagement',   action_type: 'overdue' },
];

const ACTION_CONFIG = {
  content: { bg: '#F5F3FF', color: '#6D28D9', icon: '📄', label: 'Share Paper' },
  event:   { bg: '#EFF6FF', color: '#1D4ED8', icon: '🎓', label: 'Send Invite' },
  overdue: { bg: '#FEF2F2', color: '#B91C1C', icon: '⚠️', label: 'Re-engage' },
  birthday:    { bg: '#FEF3C7', color: '#92400E', icon: '🎂', label: 'Birthday Wish' },
  anniversary: { bg: '#FDF2F8', color: '#BE185D', icon: '💍', label: 'Anniversary Wish' },
};

const ACTION_MESSAGES = {
  content: (doc) => `Dear ${doc.name},\n\nI wanted to share a relevant clinical update that aligns with your practice interests.\n\nPlease find the attached research summary. Looking forward to your thoughts.\n\n— Jijo, Team Life · Mankind Pharma`,
  event:   (doc) => `Dear ${doc.name},\n\nWe have an upcoming medical event that would be highly relevant to your area of expertise.\n\nWe would be honoured to have your participation. Please let us know your availability.\n\n— Jijo, Team Life · Mankind Pharma`,
  overdue: (doc) => `Dear ${doc.name},\n\nI hope this message finds you well. I noticed it has been a while since we last connected.\n\nI would love to reconnect and share some recent updates that may be of interest to your practice.\n\n— Jijo, Team Life · Mankind Pharma`,
};

const KPI_FILTERS = [
  { key: '',      label: 'TOTAL',        subKey: 'total',   sub: 'Life Division' },
  { key: 'A+',   label: 'A+ DOCTORS',   subKey: 'aPlus',   sub: 'High potential' },
  { key: 'engaged', label: 'ENGAGED (30D)', subKey: 'engaged', sub: null },
  { key: 'low',  label: 'AT RISK',      subKey: 'atRisk',  sub: 'No engagement 30d+' },
  { key: 'avg',  label: 'AVG SCORE',    subKey: 'avgScore', sub: '↑ 6 pts' },
];

export default function DoctorDirectory() {
  const { addNotification, setSelectedDoctor, setCurrentTab } = useAppContext();
  const { navigate } = useRouter();
  const [doctors, setDoctors] = useState(STATIC_DOCTORS);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [specFilter, setSpecFilter] = useState('');
  const [cityFilter, setCityFilter] = useState('');
  const [catFilter, setCatFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [activeKpi, setActiveKpi] = useState(null); // which KPI box is selected
  const [actionModal, setActionModal] = useState(null); // { doc, message }
  const [actionMessage, setActionMessage] = useState('');

  useEffect(() => {
    const loadDoctors = async () => {
      try {
        setLoading(true);
        const response = await api.doctors.list();
        if (response.data && Array.isArray(response.data) && response.data.length > 0) {
          setDoctors(response.data);
        }
      } catch (err) {
        console.log('Using static doctor data');
      } finally {
        setLoading(false);
      }
    };
    loadDoctors();
  }, []);

  const kpis = useMemo(() => {
    const total = doctors.length;
    const aPlus = doctors.filter(d => d.category === 'A+').length;
    const engaged = doctors.filter(d => d.status === 'high').length;
    const atRisk = doctors.filter(d => d.status === 'low').length;
    const avgScore = total > 0 ? Math.round(doctors.reduce((s, d) => s + (d.score || 0), 0) / total) : 0;
    return { total, aPlus, engaged, atRisk, avgScore };
  }, [doctors]);

  // Fix 4: KPI box click filters the table
  const handleKpiClick = (key) => {
    if (activeKpi === key) {
      // deselect — clear
      setActiveKpi(null);
      setCatFilter('');
      setStatusFilter('');
    } else {
      setActiveKpi(key);
      if (key === 'A+') { setCatFilter('A+'); setStatusFilter(''); }
      else if (key === 'engaged') { setStatusFilter('high'); setCatFilter(''); }
      else if (key === 'low') { setStatusFilter('low'); setCatFilter(''); }
      else { setCatFilter(''); setStatusFilter(''); }
    }
  };

  const filtered = useMemo(() => {
    let result = [...doctors];
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(d =>
        d.name?.toLowerCase().includes(q) ||
        d.city?.toLowerCase().includes(q) ||
        d.specialty?.toLowerCase().includes(q)
      );
    }
    if (specFilter) result = result.filter(d => d.specialty === specFilter);
    if (cityFilter) result = result.filter(d => d.city === cityFilter);
    if (catFilter) result = result.filter(d => d.category === catFilter);
    if (statusFilter) result = result.filter(d => d.status === statusFilter);
    return result;
  }, [doctors, search, specFilter, cityFilter, catFilter, statusFilter]);

  const specialties = [...new Set(doctors.map(d => d.specialty))].sort();
  const cities = [...new Set(doctors.map(d => d.city))].sort();

  const clearFilters = () => {
    setSearch(''); setSpecFilter(''); setCityFilter('');
    setCatFilter(''); setStatusFilter(''); setActiveKpi(null);
  };

  const hasFilters = search || specFilter || cityFilter || catFilter || statusFilter;

  // Fix 1: Action button opens modal
  const openActionModal = (doc) => {
    const msgFn = ACTION_MESSAGES[doc.action_type] || ACTION_MESSAGES.content;
    setActionMessage(msgFn(doc));
    setActionModal(doc);
  };

  const handleSendAction = () => {
    if (!actionModal) return;
    const cfg = ACTION_CONFIG[actionModal.action_type] || ACTION_CONFIG.content;
    addNotification(`${cfg.label} sent to ${actionModal.name} via WhatsApp`, 'success');
    setActionModal(null);
    setActionMessage('');
  };

  const getScoreColor = (score) =>
    score >= 70 ? styles.barFillGreen : score >= 40 ? styles.barFillAmber : styles.barFillRed;

  const getStatusStyle = (status) =>
    status === 'high' ? styles.statusHigh : status === 'med' ? styles.statusMed : styles.statusLow;

  const getStatusLabel = (status) =>
    status === 'high' ? 'Engaged' : status === 'med' ? 'Moderate' : 'At Risk';

  const getCatStyle = (cat) =>
    cat === 'A+' ? styles.catAPlus : styles.catA;

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    try { return new Date(dateStr).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }); }
    catch { return dateStr; }
  };

  const getInitials = (name) =>
    name.replace('Dr. ', '').split(' ').map(w => w[0]).join('').substring(0, 2);

  const openDoctorProfile = (doc) => {
    setSelectedDoctor(doc);
    setCurrentTab('doctor360');
    navigate('bu-head', 'doctor360');
  };

  const kpiValues = [
    { key: '',         label: 'TOTAL',           val: kpis.total,    sub: 'Life Division',        style: styles.kpiNavy },
    { key: 'A+',       label: 'A+ DOCTORS',      val: kpis.aPlus,    sub: 'High potential',       style: styles.kpiGold },
    { key: 'engaged',  label: 'ENGAGED (30D)',    val: kpis.engaged,  sub: `${kpis.total > 0 ? Math.round((kpis.engaged / kpis.total) * 100) : 0}% coverage`, style: styles.kpiGreen },
    { key: 'low',      label: 'AT RISK',         val: kpis.atRisk,   sub: 'No engagement 30d+',   style: styles.kpiRed },
    { key: 'avg',      label: 'AVG SCORE',        val: kpis.avgScore, sub: '↑ 6 pts',              style: styles.kpiTeal },
  ];

  return (
    <div className={styles.container}>
      <div>
        <h1 className={styles.title}>Doctor Directory</h1>
        <p className={styles.subtitle}>Manage and monitor doctor engagement across your portfolio</p>
      </div>

      {/* Fix 4: KPI boxes are now clickable filters */}
      <div className={styles.kpiRow}>
        {kpiValues.map(k => (
          <div
            key={k.key}
            className={`${styles.kpi} ${k.style} ${activeKpi === k.key && k.key !== '' && k.key !== 'avg' ? styles.kpiActive : ''} ${k.key !== '' && k.key !== 'avg' ? styles.kpiClickable : ''}`}
            onClick={() => k.key !== '' && k.key !== 'avg' && handleKpiClick(k.key)}
            title={k.key && k.key !== 'avg' ? `Click to filter by ${k.label}` : ''}
          >
            <div className={styles.kpiLabel}>{k.label}</div>
            <div className={styles.kpiValue}>{k.val}</div>
            <div className={k.key === 'avg' ? `${styles.kpiSub} ${styles.kpiSubGreen}` : styles.kpiSub}>{k.sub}</div>
            {k.key !== '' && k.key !== 'avg' && (
              <div className={styles.kpiHint}>{activeKpi === k.key ? 'Click to clear ✕' : 'Click to filter →'}</div>
            )}
          </div>
        ))}
      </div>

      {/* Fix 3: Filters with Go button */}
      <div className={styles.filters}>
        <div className={styles.searchBox}>
          <span>🔍</span>
          <input
            className={styles.searchInput}
            type="text"
            placeholder="Search doctor, city, specialty..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && e.preventDefault()}
          />
        </div>
        <select className={styles.filterSelect} value={specFilter} onChange={e => setSpecFilter(e.target.value)}>
          <option value="">All Specialties</option>
          {specialties.map(s => <option key={s} value={s}>{s}</option>)}
        </select>
        <select className={styles.filterSelect} value={cityFilter} onChange={e => setCityFilter(e.target.value)}>
          <option value="">All Cities</option>
          {cities.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
        <select className={styles.filterSelect} value={catFilter} onChange={e => setCatFilter(e.target.value)}>
          <option value="">All Categories</option>
          <option value="A+">A+ only</option>
          <option value="A">A only</option>
        </select>
        <select className={styles.filterSelect} value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
          <option value="">All Status</option>
          <option value="high">Engaged</option>
          <option value="med">Moderate</option>
          <option value="low">At Risk</option>
        </select>
        {hasFilters && (
          <button className={styles.clearBtn} onClick={clearFilters}>✕ Clear</button>
        )}
      </div>

      <div className={styles.countText}>
        {filtered.length} of {doctors.length} doctors
        {activeKpi && activeKpi !== 'avg' && (
          <span className={styles.activeFilterTag}>
            {activeKpi === 'A+' ? 'A+ Doctors' : activeKpi === 'engaged' ? 'Engaged' : 'At Risk'} ×
          </span>
        )}
      </div>

      {/* Table */}
      <div className={styles.tableWrap}>
        {loading ? (
          <div className={styles.loading}><div className={styles.spinner} /><span>Loading doctors...</span></div>
        ) : filtered.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>👨‍⚕️</div>
            <p className={styles.emptyText}>No doctors match your filters</p>
            <button className={styles.clearBtn} style={{ marginTop: 12 }} onClick={clearFilters}>Clear Filters</button>
          </div>
        ) : (
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Doctor</th>
                <th>City</th>
                <th>Cat.</th>
                <th>DM Score</th>
                <th>SOW %</th>
                <th>Score</th>
                <th>Status</th>
                <th>Last Engaged</th>
                <th>Recommended Action</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(doc => {
                const cfg = ACTION_CONFIG[doc.action_type] || ACTION_CONFIG.content;
                return (
                  <tr key={doc.id}>
                    <td>
                      <div className={styles.docCell}>
                        <div className={styles.docAvatar}>{getInitials(doc.name)}</div>
                        <div>
                          <button className={styles.docNameLink} onClick={() => openDoctorProfile(doc)}>
                            {doc.name}
                          </button>
                          <div className={styles.docSpecialty}>{doc.specialty}</div>
                        </div>
                      </div>
                    </td>
                    <td>{doc.city}</td>
                    <td><span className={`${styles.catPill} ${getCatStyle(doc.category)}`}>{doc.category}</span></td>
                    <td style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700 }}>{doc.dm_score}</td>
                    <td style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700 }}>{doc.sow}%</td>
                    <td>
                      <div className={styles.scoreBar}>
                        <div className={styles.barTrack}>
                          <div className={`${styles.barFill} ${getScoreColor(doc.score)}`} style={{ width: `${doc.score}%` }} />
                        </div>
                        <span className={styles.scoreVal}>{doc.score}</span>
                      </div>
                    </td>
                    <td><span className={getStatusStyle(doc.status)}>{getStatusLabel(doc.status)}</span></td>
                    <td>{formatDate(doc.last_engaged)}</td>
                    {/* Fix 1: Action button with onClick */}
                    <td>
                      <button
                        className={styles.actionBtn}
                        style={{ background: cfg.bg, color: cfg.color }}
                        onClick={() => openActionModal(doc)}
                      >
                        <span>{cfg.icon}</span>
                        <span>{doc.next_action}</span>
                        <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                          <path d="M2 5h6M5 2l3 3-3 3"/>
                        </svg>
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Action Modal */}
      {actionModal && (() => {
        const cfg = ACTION_CONFIG[actionModal.action_type] || ACTION_CONFIG.content;
        return (
          <div className={styles.modalOverlay} onClick={e => { if (e.target === e.currentTarget) setActionModal(null); }}>
            <div className={styles.modalCard}>
              <div className={styles.modalHeader}>
                <div className={styles.modalIcon} style={{ background: cfg.bg }}>{cfg.icon}</div>
                <div style={{ flex: 1 }}>
                  <div className={styles.modalTitle}>{cfg.label} · {actionModal.name}</div>
                  <div className={styles.modalSub}>{actionModal.specialty} · {actionModal.city} · {actionModal.category} · Score {actionModal.score}</div>
                </div>
                <button className={styles.modalClose} onClick={() => setActionModal(null)}>✕</button>
              </div>
              <div className={styles.modalBody}>
                <div className={styles.modalLabel}>Channel</div>
                <div style={{ marginBottom: 14 }}>
                  <span className={styles.channelBadge}>💬 WhatsApp</span>
                </div>
                <div className={styles.modalLabel}>Message</div>
                <textarea
                  className={styles.modalTextarea}
                  value={actionMessage}
                  onChange={e => setActionMessage(e.target.value)}
                  rows={7}
                />
                <div className={styles.modalLabel}>Action</div>
                <div className={styles.modalActionInfo}>
                  <strong>{actionModal.next_action}</strong>
                </div>
              </div>
              <div className={styles.modalFooter}>
                <button className={styles.modalCancelBtn} onClick={() => setActionModal(null)}>Cancel</button>
                <button className={styles.modalSendBtn} onClick={handleSendAction}>
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M11.5 1L1 5l4 2 2 4 4.5-10z"/>
                  </svg>
                  Send via WhatsApp
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
