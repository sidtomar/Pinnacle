import React, { useState, useMemo } from 'react';
import styles from './Analytics.module.css';

const ANALYTICS_DATA = [
  { id: 1, name: 'Dr. Priya Sharma', specialty: 'Gynaecology', city: 'Mumbai', division: 'Life', category: 'A+', dms_prev: 32, dms_curr: 42, sow_prev: 28, sow_curr: 35, engagements: 14, trend: 'up' },
  { id: 2, name: 'Dr. Rajesh Patel', specialty: 'Cardiology', city: 'Delhi', division: 'Life', category: 'A+', dms_prev: 45, dms_curr: 55, sow_prev: 38, sow_curr: 48, engagements: 22, trend: 'up' },
  { id: 3, name: 'Dr. Anjali Desai', specialty: 'Paediatrics', city: 'Bangalore', division: 'Life', category: 'A', dms_prev: 30, dms_curr: 33, sow_prev: 25, sow_curr: 27, engagements: 8, trend: 'flat' },
  { id: 4, name: 'Dr. Vikram Singh', specialty: 'Oncology', city: 'Chennai', division: 'Specialty', category: 'A+', dms_prev: 40, dms_curr: 48, sow_prev: 35, sow_curr: 42, engagements: 18, trend: 'up' },
  { id: 5, name: 'Dr. Meera Krishnan', specialty: 'Dermatology', city: 'Hyderabad', division: 'Life', category: 'A', dms_prev: 28, dms_curr: 25, sow_prev: 22, sow_curr: 20, engagements: 5, trend: 'down' },
  { id: 6, name: 'Dr. Arun Gupta', specialty: 'Cardiology', city: 'Kolkata', division: 'Life', category: 'A', dms_prev: 22, dms_curr: 18, sow_prev: 18, sow_curr: 15, engagements: 3, trend: 'down' },
  { id: 7, name: 'Dr. Sunita Reddy', specialty: 'Neurology', city: 'Pune', division: 'Specialty', category: 'A+', dms_prev: 48, dms_curr: 52, sow_prev: 40, sow_curr: 45, engagements: 20, trend: 'up' },
  { id: 8, name: 'Dr. Karan Mehta', specialty: 'Gynaecology', city: 'Ahmedabad', division: 'Life', category: 'A', dms_prev: 35, dms_curr: 35, sow_prev: 28, sow_curr: 29, engagements: 9, trend: 'flat' },
  { id: 9, name: 'Dr. Nisha Joshi', specialty: 'Paediatrics', city: 'Mumbai', division: 'Life', category: 'A+', dms_prev: 38, dms_curr: 44, sow_prev: 32, sow_curr: 38, engagements: 16, trend: 'up' },
  { id: 10, name: 'Dr. Rahul Verma', specialty: 'Cardiology', city: 'Delhi', division: 'Life', category: 'A', dms_prev: 18, dms_curr: 15, sow_prev: 14, sow_curr: 12, engagements: 2, trend: 'down' }
];

export default function Analytics() {
  const [period, setPeriod] = useState('6m');
  const [search, setSearch] = useState('');
  const [specFilter, setSpecFilter] = useState('');
  const [catFilter, setCatFilter] = useState('');
  const [trendFilter, setTrendFilter] = useState('');

  const filtered = useMemo(() => {
    let result = [...ANALYTICS_DATA];
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(d => d.name.toLowerCase().includes(q) || d.city.toLowerCase().includes(q));
    }
    if (specFilter) result = result.filter(d => d.specialty === specFilter);
    if (catFilter) result = result.filter(d => d.category === catFilter);
    if (trendFilter) result = result.filter(d => d.trend === trendFilter);
    return result;
  }, [search, specFilter, catFilter, trendFilter]);

  const specialties = [...new Set(ANALYTICS_DATA.map(d => d.specialty))];

  const kpis = useMemo(() => {
    const totalDocs = ANALYTICS_DATA.length;
    const avgDMS = Math.round(ANALYTICS_DATA.reduce((s, d) => s + d.dms_curr, 0) / totalDocs);
    const avgSOW = Math.round(ANALYTICS_DATA.reduce((s, d) => s + d.sow_curr, 0) / totalDocs);
    const totalEng = ANALYTICS_DATA.reduce((s, d) => s + d.engagements, 0);
    const trendingUp = ANALYTICS_DATA.filter(d => d.trend === 'up').length;
    return { totalDocs, avgDMS, avgSOW, totalEng, trendingUp };
  }, []);

  const getInitials = (name) => name.replace('Dr. ', '').split(' ').map(w => w[0]).join('').substring(0, 2);

  const getDelta = (prev, curr) => {
    const diff = curr - prev;
    const pct = prev > 0 ? Math.round((diff / prev) * 100) : 0;
    return { diff, pct, direction: diff > 0 ? 'up' : diff < 0 ? 'down' : 'flat' };
  };

  const getTrendBadge = (trend) => {
    if (trend === 'up') return { class: styles.trendBadgeUp, label: '↑ Trending Up' };
    if (trend === 'down') return { class: styles.trendBadgeDown, label: '↓ Declining' };
    return { class: styles.trendBadgeFlat, label: '→ Flat' };
  };

  const getCatStyle = (cat) => {
    if (cat === 'A+') return styles.catAPlus;
    if (cat === 'A') return styles.catA;
    return styles.catB;
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Engagement Impact Analytics</h1>
          <p className={styles.subtitle}>How engagement activities are moving DMS & Share of Wallet across your doctor portfolio</p>
        </div>
        <div className={styles.headerActions}>
          <select className={styles.periodSelect} value={period} onChange={e => setPeriod(e.target.value)}>
            <option value="3m">Last 3 months</option>
            <option value="6m">Last 6 months</option>
            <option value="12m">Last 12 months</option>
            <option value="ytd">Year to date</option>
          </select>
          <button className={styles.exportBtn}>📥 Export</button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <div className={`${styles.kpiAccent} ${styles.accentNavy}`} />
          <div className={styles.kpiLabel}>Portfolio Size</div>
          <div className={styles.kpiValue}>{kpis.totalDocs}</div>
          <div className={styles.kpiSub}>Active doctors <span className={`${styles.kpiDelta} ${styles.deltaUp}`}>↑ 4%</span></div>
        </div>
        <div className={styles.kpiCard}>
          <div className={`${styles.kpiAccent} ${styles.accentGold}`} />
          <div className={styles.kpiLabel}>Avg DMS Score</div>
          <div className={styles.kpiValue}>{kpis.avgDMS}</div>
          <div className={styles.kpiSub}>vs last period <span className={`${styles.kpiDelta} ${styles.deltaUp}`}>↑ 8%</span></div>
        </div>
        <div className={styles.kpiCard}>
          <div className={`${styles.kpiAccent} ${styles.accentGreen}`} />
          <div className={styles.kpiLabel}>Avg SOW %</div>
          <div className={styles.kpiValue}>{kpis.avgSOW}%</div>
          <div className={styles.kpiSub}>Share of wallet <span className={`${styles.kpiDelta} ${styles.deltaUp}`}>↑ 5%</span></div>
        </div>
        <div className={styles.kpiCard}>
          <div className={`${styles.kpiAccent} ${styles.accentTeal}`} />
          <div className={styles.kpiLabel}>Total Engagements</div>
          <div className={styles.kpiValue}>{kpis.totalEng}</div>
          <div className={styles.kpiSub}>{kpis.trendingUp} trending up <span className={`${styles.kpiDelta} ${styles.deltaUp}`}>↑ 12%</span></div>
        </div>
      </div>

      {/* AI Insight */}
      <div className={styles.insight}>
        <div className={styles.insightIcon}>✨</div>
        <div>
          <div className={styles.insightTitle}>AI-Powered Insight</div>
          <div className={styles.insightBody}>
            Doctors with 10+ content engagements show 23% higher DMS growth vs baseline. Focus content sharing on the 3 "At Risk" doctors — Dr. Meera K., Dr. Arun G., and Dr. Rahul V. — to recover declining SOW trends.
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className={styles.controls}>
        <div className={styles.filterGroup}>
          <div className={styles.searchBox}>
            <span>🔍</span>
            <input className={styles.searchInput} type="text" placeholder="Search doctor, city..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <select className={styles.filterSelect} value={specFilter} onChange={e => setSpecFilter(e.target.value)}>
            <option value="">All specialties</option>
            {specialties.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
          <select className={styles.filterSelect} value={catFilter} onChange={e => setCatFilter(e.target.value)}>
            <option value="">All categories</option>
            <option value="A+">A+</option>
            <option value="A">A</option>
          </select>
          <select className={styles.filterSelect} value={trendFilter} onChange={e => setTrendFilter(e.target.value)}>
            <option value="">All trends</option>
            <option value="up">Trending up</option>
            <option value="flat">Flat</option>
            <option value="down">Declining</option>
          </select>
        </div>
        <span className={styles.countLabel}>Showing <span className={styles.countValue}>{filtered.length}</span> doctors</span>
      </div>

      {/* Table */}
      <div className={styles.tableWrap}>
        <div className={styles.tableScroll}>
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Doctor</th>
                <th>Cat.</th>
                <th>DMS (Prev)</th>
                <th>DMS (Curr)</th>
                <th>Δ DMS</th>
                <th>SOW (Prev)</th>
                <th>SOW (Curr)</th>
                <th>Δ SOW</th>
                <th>Engagements</th>
                <th>Trend</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(doc => {
                const dmsDelta = getDelta(doc.dms_prev, doc.dms_curr);
                const sowDelta = getDelta(doc.sow_prev, doc.sow_curr);
                const trendBadge = getTrendBadge(doc.trend);
                return (
                  <tr key={doc.id}>
                    <td>
                      <div className={styles.docCell}>
                        <div className={styles.docAvatar}>{getInitials(doc.name)}</div>
                        <div>
                          <div className={styles.docName}>{doc.name}</div>
                          <div className={styles.docMeta}>{doc.specialty} · {doc.city}</div>
                        </div>
                      </div>
                    </td>
                    <td><span className={`${styles.catPill} ${getCatStyle(doc.category)}`}>{doc.category}</span></td>
                    <td className={styles.numCell}>{doc.dms_prev}</td>
                    <td className={styles.numCell}>{doc.dms_curr}</td>
                    <td><span className={dmsDelta.direction === 'up' ? styles.trendUp : dmsDelta.direction === 'down' ? styles.trendDown : styles.trendFlat} style={{ fontWeight: 700 }}>{dmsDelta.diff > 0 ? '+' : ''}{dmsDelta.diff} ({dmsDelta.pct}%)</span></td>
                    <td className={styles.numCell}>{doc.sow_prev}%</td>
                    <td className={styles.numCell}>{doc.sow_curr}%</td>
                    <td><span className={sowDelta.direction === 'up' ? styles.trendUp : sowDelta.direction === 'down' ? styles.trendDown : styles.trendFlat} style={{ fontWeight: 700 }}>{sowDelta.diff > 0 ? '+' : ''}{sowDelta.diff}pp</span></td>
                    <td className={styles.numCell}>{doc.engagements}</td>
                    <td><span className={trendBadge.class}>{trendBadge.label}</span></td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <div className={styles.tableFoot}>
          <span>Avg DMS: {Math.round(filtered.reduce((s, d) => s + d.dms_curr, 0) / (filtered.length || 1))} · Avg SOW: {Math.round(filtered.reduce((s, d) => s + d.sow_curr, 0) / (filtered.length || 1))}%</span>
          <span>Tip: Click any doctor row to open 360° view</span>
        </div>
      </div>
    </div>
  );
}
