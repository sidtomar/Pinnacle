import React, { useState, useCallback } from 'react';
import { useAppContext } from '../../hooks/useAppContext';
import styles from './Dashboard.module.css';

const CONTENT_DATA = [
  { id: 1, title: 'SGLT2 Inhibitors in Heart Failure: 2024 Update', status: 'approved', source: 'ai', specialty: 'Cardiology', created: '2024-12-10', reviewed: '2024-12-11', shares: 12, channel: 'whatsapp' },
  { id: 2, title: 'GLP-1 RA Cardiovascular Benefits Beyond Glucose', status: 'approved', source: 'ai', specialty: 'Diabetology', created: '2024-12-09', reviewed: '2024-12-10', shares: 8, channel: 'email' },
  { id: 3, title: 'Iron Deficiency Management in Pregnancy', status: 'approved', source: 'manual', specialty: 'Gynaecology', created: '2024-12-08', reviewed: '2024-12-09', shares: 15, channel: 'whatsapp' },
  { id: 4, title: 'Paediatric Immunisation Schedule 2024-25', status: 'pending', source: 'ai', specialty: 'Paediatrics', created: '2024-12-07', reviewed: null, shares: 0, channel: null },
  { id: 5, title: 'Biologics in Moderate-to-Severe Acne', status: 'approved', source: 'ai', specialty: 'Dermatology', created: '2024-12-06', reviewed: '2024-12-07', shares: 6, channel: 'whatsapp' },
  { id: 6, title: 'Hypertension Guidelines: ACEi vs ARB Selection', status: 'approved', source: 'manual', specialty: 'Cardiology', created: '2024-12-05', reviewed: '2024-12-06', shares: 10, channel: 'email' },
  { id: 7, title: 'PCOS: Lifestyle vs Pharmacological Interventions', status: 'rejected', source: 'ai', specialty: 'Gynaecology', created: '2024-12-04', reviewed: '2024-12-05', shares: 0, channel: null },
  { id: 8, title: 'Thyroid Disorders in Pregnancy', status: 'approved', source: 'ai', specialty: 'Endocrinology', created: '2024-12-03', reviewed: '2024-12-04', shares: 9, channel: 'whatsapp' },
  { id: 9, title: 'Statins: Latest Evidence on Myopathy Risk', status: 'pending', source: 'manual', specialty: 'Cardiology', created: '2024-12-02', reviewed: null, shares: 0, channel: null },
  { id: 10, title: 'Vitamin D Supplementation in Paediatrics', status: 'approved', source: 'ai', specialty: 'Paediatrics', created: '2024-12-01', reviewed: '2024-12-02', shares: 7, channel: 'email' },
];

const DOCTOR_DATA = [
  { name: 'Dr. Rajesh Kumar', specialty: 'Cardiology', articlesReceived: 5, lastShared: '2024-12-10' },
  { name: 'Dr. Priya Sharma', specialty: 'Diabetology', articlesReceived: 3, lastShared: '2024-12-09' },
  { name: 'Dr. Anita Desai', specialty: 'Gynaecology', articlesReceived: 4, lastShared: '2024-12-08' },
  { name: 'Dr. Vikram Singh', specialty: 'Paediatrics', articlesReceived: 2, lastShared: '2024-12-07' },
  { name: 'Dr. Meena Patel', specialty: 'Dermatology', articlesReceived: 3, lastShared: '2024-12-06' },
];

const SHARING_REPORT = [
  { sno: 1, title: 'SGLT2 Inhibitors in Heart Failure: 2024 Update', created: '10 Dec 2024', reviewed: '11 Dec 2024', shared: '12 Dec 2024', doctor: 'Dr. Rajesh Kumar', specialty: 'Cardiology', channel: 'whatsapp' },
  { sno: 2, title: 'GLP-1 RA Cardiovascular Benefits Beyond Glucose', created: '09 Dec 2024', reviewed: '10 Dec 2024', shared: '11 Dec 2024', doctor: 'Dr. Priya Sharma', specialty: 'Diabetology', channel: 'email' },
  { sno: 3, title: 'Iron Deficiency Management in Pregnancy', created: '08 Dec 2024', reviewed: '09 Dec 2024', shared: '10 Dec 2024', doctor: 'Dr. Anita Desai', specialty: 'Gynaecology', channel: 'whatsapp' },
  { sno: 4, title: 'Biologics in Moderate-to-Severe Acne', created: '06 Dec 2024', reviewed: '07 Dec 2024', shared: '08 Dec 2024', doctor: 'Dr. Meena Patel', specialty: 'Dermatology', channel: 'whatsapp' },
  { sno: 5, title: 'Hypertension Guidelines: ACEi vs ARB Selection', created: '05 Dec 2024', reviewed: '06 Dec 2024', shared: '07 Dec 2024', doctor: 'Dr. Rajesh Kumar', specialty: 'Cardiology', channel: 'email' },
  { sno: 6, title: 'Thyroid Disorders in Pregnancy', created: '03 Dec 2024', reviewed: '04 Dec 2024', shared: '05 Dec 2024', doctor: 'Dr. Anita Desai', specialty: 'Gynaecology', channel: 'whatsapp' },
  { sno: 7, title: 'Vitamin D Supplementation in Paediatrics', created: '01 Dec 2024', reviewed: '02 Dec 2024', shared: '03 Dec 2024', doctor: 'Dr. Vikram Singh', specialty: 'Paediatrics', channel: 'email' },
];

const TIMELINE_EVENTS = [
  { icon: '\u{1F4DD}', bg: '#EFF6FF', color: '#3B82F6', title: 'Article Created', desc: 'SGLT2 Inhibitors in Heart Failure: 2024 Update', time: '2 hours ago' },
  { icon: '✅', bg: '#ECFDF5', color: '#10B981', title: 'MA Approved', desc: 'GLP-1 RA Cardiovascular Benefits Beyond Glucose', time: '4 hours ago' },
  { icon: '\u{1F4E4}', bg: '#FEF3C7', color: '#D97706', title: 'Shared via WhatsApp', desc: 'Iron Deficiency Management to Dr. Anita Desai', time: '6 hours ago' },
  { icon: '\u{1F916}', bg: '#F3E8FF', color: '#7C3AED', title: 'Pipeline Completed', desc: 'Biologics in Moderate-to-Severe Acne', time: 'Yesterday' },
  { icon: '\u{1F464}', bg: '#FFF7ED', color: '#EA580C', title: 'Doctor Synced', desc: '3 new doctors added from CRM', time: 'Yesterday' },
  { icon: '\u{1F4E7}', bg: '#EFF6FF', color: '#3B82F6', title: 'Shared via Email', desc: 'Hypertension Guidelines to Dr. Rajesh Kumar', time: '2 days ago' },
  { icon: '❌', bg: '#FEF2F2', color: '#EF4444', title: 'Article Rejected', desc: 'PCOS: Lifestyle vs Pharmacological Interventions', time: '2 days ago' },
  { icon: '\u{1F50D}', bg: '#ECFDF5', color: '#10B981', title: 'PubMed Sync', desc: '5 new articles found for Cardiology topics', time: '3 days ago' },
];

const KPI_CONFIG = [
  { key: 'total', label: 'Articles Created', sub: 'Total in library', accent: 'var(--blue)' },
  { key: 'ai', label: 'AI-Generated', sub: '% of total', accent: '#7C3AED' },
  { key: 'approved', label: 'MA Approved', sub: 'Approval rate', accent: 'var(--green)' },
  { key: 'doctors', label: 'Doctors Reached', sub: 'Unique HCPs', accent: '#D97706' },
  { key: 'shares', label: 'Total Shares', sub: 'via WhatsApp & Email', accent: 'var(--navy)' },
];

const PIPELINE_STATUS = [
  { label: 'Approved', count: 7, pct: 70, color: 'var(--green)' },
  { label: 'Pending Review', count: 2, pct: 20, color: '#D97706' },
  { label: 'Rejected', count: 1, pct: 10, color: 'var(--red)' },
];

const SHARING_CHANNELS = [
  { label: 'WhatsApp', count: 46, pct: 68, color: '#10B981' },
  { label: 'Email', count: 21, pct: 32, color: '#3B82F6' },
];

const PIPELINE_PERF = [
  { label: 'Total Runs', value: '24' },
  { label: 'Success Rate', value: '91.7%' },
  { label: 'Avg. Duration', value: '8.2s' },
  { label: 'Articles Generated', value: '22' },
];

const SPECIALTY_COVERAGE = [
  { label: 'Cardiology', count: 15, pct: 85, color: 'var(--blue)' },
  { label: 'Diabetology', count: 10, pct: 65, color: '#7C3AED' },
  { label: 'Gynaecology', count: 8, pct: 55, color: '#EC4899' },
  { label: 'Paediatrics', count: 6, pct: 40, color: '#10B981' },
  { label: 'Dermatology', count: 5, pct: 35, color: '#D97706' },
];

export default function Dashboard() {
  const { addNotification } = useAppContext();
  const [activeKpi, setActiveKpi] = useState(null);
  const [filters, setFilters] = useState({ article: '', party: '', channel: '' });
  const [downloading, setDownloading] = useState(false);

  const handleDownloadReport = useCallback(async () => {
    setDownloading(true);
    try {
      const resp = await fetch('http://localhost:8010/report/download');
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || 'Server returned ' + resp.status);
      }
      const blob = await resp.blob();
      const cd = resp.headers.get('content-disposition') || '';
      const match = cd.match(/filename="?([^"]+)"?/);
      const filename = match ? match[1] : 'PinnacleIQ_Business_Report.xlsx';
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
      addNotification('Business Report downloaded successfully', 'success');
    } catch (e) {
      console.error('Report download failed:', e);
      addNotification(e.message || 'Failed to generate report', 'error');
    } finally {
      setDownloading(false);
    }
  }, [addNotification]);

  // Compute KPI values
  const totalArticles = CONTENT_DATA.length;
  const aiGenerated = CONTENT_DATA.filter(c => c.source === 'ai').length;
  const approved = CONTENT_DATA.filter(c => c.status === 'approved').length;
  const doctorsReached = DOCTOR_DATA.length;
  const totalShares = CONTENT_DATA.reduce((s, c) => s + c.shares, 0);

  const kpiValues = {
    total: totalArticles,
    ai: aiGenerated,
    approved: approved,
    doctors: doctorsReached,
    shares: totalShares,
  };

  const kpiSubs = {
    total: 'Total in library',
    ai: `${Math.round((aiGenerated / totalArticles) * 100)}% of total`,
    approved: `${Math.round((approved / totalArticles) * 100)}% approval rate`,
    doctors: 'Unique HCPs',
    shares: 'via WhatsApp & Email',
  };

  const handleKpiClick = (key) => {
    setActiveKpi(activeKpi === key ? null : key);
  };

  const getDetailData = () => {
    switch (activeKpi) {
      case 'total':
        return { title: 'All Articles', items: CONTENT_DATA, columns: ['Title', 'Status', 'Source', 'Specialty', 'Created'] };
      case 'ai':
        return { title: 'AI-Generated Articles', items: CONTENT_DATA.filter(c => c.source === 'ai'), columns: ['Title', 'Status', 'Specialty', 'Created'] };
      case 'approved':
        return { title: 'MA Approved Articles', items: CONTENT_DATA.filter(c => c.status === 'approved'), columns: ['Title', 'Specialty', 'Reviewed', 'Shares'] };
      case 'doctors':
        return { title: 'Doctors Reached', items: DOCTOR_DATA, columns: ['Name', 'Specialty', 'Articles Received', 'Last Shared'] };
      case 'shares':
        return { title: 'Sharing Activity', items: CONTENT_DATA.filter(c => c.shares > 0), columns: ['Title', 'Channel', 'Shares', 'Specialty'] };
      default:
        return null;
    }
  };

  const filteredReport = SHARING_REPORT.filter(row => {
    if (filters.article && !row.title.toLowerCase().includes(filters.article.toLowerCase())) return false;
    if (filters.party && !row.doctor.toLowerCase().includes(filters.party.toLowerCase()) && !row.specialty.toLowerCase().includes(filters.party.toLowerCase())) return false;
    if (filters.channel && row.channel !== filters.channel) return false;
    return true;
  });

  const detailData = getDetailData();

  return (
    <div className={styles.container}>
      {/* Hero Banner */}
      <div className={styles.heroBanner}>
        <div className={styles.heroContent}>
          <div>
            <h1 className={styles.heroTitle}>PinnacleIQ &middot; Dashboard</h1>
            <p className={styles.heroSub}>AI-Powered Doctor Intelligence Platform &middot; Mankind Pharma</p>
          </div>
          <div className={styles.heroActions}>
            <button
              className={styles.downloadBtn}
              onClick={handleDownloadReport}
              disabled={downloading}
            >
              {downloading ? (
                <>
                  <span className={styles.btnSpinner}></span>
                  Generating...
                </>
              ) : (
                <>
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M4 12h8M8 2v8M5 7l3 3 3-3"/></svg>
                  Download Report
                </>
              )}
            </button>
            <button className={styles.refreshBtn} onClick={() => addNotification('Dashboard data refreshed', 'success')}>
              Refresh Data
            </button>
          </div>
        </div>
      </div>

      {/* 5 Clickable KPI Cards */}
      <div className={styles.kpiRow}>
        {KPI_CONFIG.map(kpi => (
          <div
            key={kpi.key}
            className={`${styles.kpiCard} ${activeKpi === kpi.key ? styles.kpiActive : ''}`}
            onClick={() => handleKpiClick(kpi.key)}
          >
            <div className={styles.kpiAccent} style={{ background: kpi.accent }}></div>
            <div className={styles.kpiValue}>{kpiValues[kpi.key]}</div>
            <div className={styles.kpiLabel}>{kpi.label}</div>
            <div className={styles.kpiSub}>{kpiSubs[kpi.key]}</div>
            <span className={styles.clickHint}>Click to view</span>
          </div>
        ))}
      </div>

      {/* Detail Table (shown when KPI clicked) */}
      {activeKpi && detailData && (
        <div className={styles.detailPanel}>
          <div className={styles.detailHeader}>
            <div className={styles.detailHeaderLeft}>
              <span className={styles.detailTitle}>{detailData.title}</span>
              <span className={styles.detailCount}>{detailData.items.length} items</span>
            </div>
            <button className={styles.closeBtn} onClick={() => setActiveKpi(null)}>Close</button>
          </div>
          <div className={styles.detailTableWrap}>
            <table className={styles.detailTable}>
              <thead>
                <tr>
                  {detailData.columns.map(col => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {activeKpi === 'doctors' ? (
                  detailData.items.map((doc, i) => (
                    <tr key={i}>
                      <td className={styles.cellBold}>{doc.name}</td>
                      <td>{doc.specialty}</td>
                      <td>{doc.articlesReceived}</td>
                      <td>{doc.lastShared}</td>
                    </tr>
                  ))
                ) : (
                  detailData.items.map((item, i) => (
                    <tr key={i}>
                      <td className={styles.cellBold}>{item.title}</td>
                      {detailData.columns.includes('Status') && (
                        <td><span className={`${styles.statusBadge} ${styles['status_' + item.status]}`}>{item.status}</span></td>
                      )}
                      {detailData.columns.includes('Source') && (
                        <td><span className={item.source === 'ai' ? styles.srcAi : styles.srcManual}>{item.source === 'ai' ? 'AI' : 'Manual'}</span></td>
                      )}
                      {detailData.columns.includes('Channel') && (
                        <td><span className={`${styles.channelBadge} ${item.channel === 'whatsapp' ? styles.chWa : styles.chEm}`}>{item.channel === 'whatsapp' ? 'WhatsApp' : 'Email'}</span></td>
                      )}
                      {detailData.columns.includes('Specialty') && <td>{item.specialty}</td>}
                      {detailData.columns.includes('Created') && <td>{item.created}</td>}
                      {detailData.columns.includes('Reviewed') && <td>{item.reviewed || '—'}</td>}
                      {detailData.columns.includes('Shares') && <td className={styles.cellBold}>{item.shares}</td>}
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
          <div className={styles.detailFooter}>Sorted by most recent first</div>
        </div>
      )}

      {/* 2x2 Grid */}
      <div className={styles.gridTwo}>
        {/* Content Pipeline Status */}
        <div className={styles.gridCard}>
          <div className={styles.gridCardTitle}>Content Pipeline Status</div>
          {PIPELINE_STATUS.map((bar, i) => (
            <div key={i} className={styles.barRow}>
              <span className={styles.barLabel}>{bar.label}</span>
              <div className={styles.barTrack}>
                <div className={styles.barFill} style={{ width: `${bar.pct}%`, background: bar.color }}></div>
              </div>
              <span className={styles.barCount}>{bar.count}</span>
              <span className={styles.barPct}>{bar.pct}%</span>
            </div>
          ))}
        </div>

        {/* Sharing Activity */}
        <div className={styles.gridCard}>
          <div className={styles.gridCardTitle}>Sharing Activity</div>
          {SHARING_CHANNELS.map((bar, i) => (
            <div key={i} className={styles.barRow}>
              <span className={styles.barLabel}>{bar.label}</span>
              <div className={styles.barTrack}>
                <div className={styles.barFill} style={{ width: `${bar.pct}%`, background: bar.color }}></div>
              </div>
              <span className={styles.barCount}>{bar.count}</span>
              <span className={styles.barPct}>{bar.pct}%</span>
            </div>
          ))}
        </div>

        {/* AI Pipeline Performance */}
        <div className={styles.gridCard}>
          <div className={styles.gridCardTitle}>AI Pipeline Performance</div>
          {PIPELINE_PERF.map((stat, i) => (
            <div key={i} className={styles.statRow}>
              <span className={styles.statLabel}>{stat.label}</span>
              <span className={styles.statValue}>{stat.value}</span>
            </div>
          ))}
        </div>

        {/* Doctor Coverage */}
        <div className={styles.gridCard}>
          <div className={styles.gridCardTitle}>Doctor Coverage by Specialty</div>
          {SPECIALTY_COVERAGE.map((bar, i) => (
            <div key={i} className={styles.barRow}>
              <span className={styles.barLabel}>{bar.label}</span>
              <div className={styles.barTrack}>
                <div className={styles.barFill} style={{ width: `${bar.pct}%`, background: bar.color }}></div>
              </div>
              <span className={styles.barCount}>{bar.count}</span>
              <span className={styles.barPct}>{bar.pct}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* Sharing Report Section */}
      <div className={styles.reportSection}>
        <div className={styles.reportHeader}>
          <div>
            <h2 className={styles.reportTitle}>Sharing Report</h2>
            <p className={styles.reportSub}>Track all content distributed to doctors &middot; filter by any column</p>
          </div>
          <div className={styles.reportActions}>
            <button className={styles.outlineBtn}>Refresh</button>
            <button className={styles.navyBtn}>Export CSV</button>
          </div>
        </div>

        {/* Report KPIs */}
        <div className={styles.reportKpis}>
          <div className={styles.reportKpi}>
            <div className={styles.reportKpiVal}>{totalShares}</div>
            <div className={styles.reportKpiLabel}>Total Shares</div>
          </div>
          <div className={styles.reportKpi}>
            <div className={styles.reportKpiVal}>{SHARING_REPORT.length}</div>
            <div className={styles.reportKpiLabel}>Unique Articles</div>
          </div>
          <div className={styles.reportKpi}>
            <div className={styles.reportKpiVal}>{doctorsReached}</div>
            <div className={styles.reportKpiLabel}>Unique Doctors</div>
          </div>
          <div className={styles.reportKpi}>
            <div className={styles.reportKpiVal}>{SHARING_REPORT.filter(r => r.shared.includes('Dec')).length}</div>
            <div className={styles.reportKpiLabel}>Shared This Month</div>
          </div>
        </div>

        {/* Sharing Table */}
        <div className={styles.tableCard}>
          <div className={styles.tableWrap}>
            <table className={styles.srTable}>
              <thead>
                <tr>
                  <th style={{ width: 52 }}>S.No</th>
                  <th>Article Title</th>
                  <th style={{ width: 120 }}>Creation Date</th>
                  <th style={{ width: 120 }}>Review Date</th>
                  <th style={{ width: 120 }}>Shared Date</th>
                  <th>Party Details</th>
                </tr>
                <tr className={styles.filterRow}>
                  <td></td>
                  <td>
                    <input
                      className={styles.filterInput}
                      placeholder="Search title..."
                      value={filters.article}
                      onChange={e => setFilters(f => ({ ...f, article: e.target.value }))}
                    />
                  </td>
                  <td></td>
                  <td></td>
                  <td></td>
                  <td className={styles.filterPartyCell}>
                    <input
                      className={styles.filterInput}
                      placeholder="Doctor / specialty..."
                      value={filters.party}
                      onChange={e => setFilters(f => ({ ...f, party: e.target.value }))}
                    />
                    <select
                      className={styles.filterInput}
                      style={{ width: 100 }}
                      value={filters.channel}
                      onChange={e => setFilters(f => ({ ...f, channel: e.target.value }))}
                    >
                      <option value="">All</option>
                      <option value="whatsapp">WhatsApp</option>
                      <option value="email">Email</option>
                    </select>
                    <button className={styles.clearBtn} onClick={() => setFilters({ article: '', party: '', channel: '' })}>Clear</button>
                  </td>
                </tr>
              </thead>
              <tbody>
                {filteredReport.map(row => (
                  <tr key={row.sno}>
                    <td>{row.sno}</td>
                    <td className={styles.cellBold}>{row.title}</td>
                    <td>{row.created}</td>
                    <td>{row.reviewed}</td>
                    <td>{row.shared}</td>
                    <td>
                      <div>{row.doctor}</div>
                      <div className={styles.partyMeta}>
                        {row.specialty}
                        <span className={`${styles.channelBadge} ${row.channel === 'whatsapp' ? styles.chWa : styles.chEm}`}>
                          {row.channel === 'whatsapp' ? 'WhatsApp' : 'Email'}
                        </span>
                      </div>
                    </td>
                  </tr>
                ))}
                {filteredReport.length === 0 && (
                  <tr><td colSpan="6" className={styles.emptyCell}>No matching records</td></tr>
                )}
              </tbody>
            </table>
          </div>
          <div className={styles.tableFooter}>
            Showing {filteredReport.length} of {SHARING_REPORT.length} records
          </div>
        </div>
      </div>

      {/* Recent Activity Timeline */}
      <div className={styles.timelineCard}>
        <div className={styles.gridCardTitle}>
          Recent Activity
          <span className={styles.timelineSub}>Last 10 events across all platform actions</span>
        </div>
        {TIMELINE_EVENTS.map((ev, i) => (
          <div key={i} className={styles.tlItem}>
            <div className={styles.tlDot} style={{ background: ev.bg, color: ev.color }}>{ev.icon}</div>
            <div className={styles.tlContent}>
              <div className={styles.tlTitle}>{ev.title}</div>
              <div className={styles.tlDesc}>{ev.desc}</div>
            </div>
            <div className={styles.tlTime}>{ev.time}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
