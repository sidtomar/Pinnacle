import React, { useState } from 'react';
import { useAppContext } from '../../hooks/useAppContext';
import styles from './Doctor360.module.css';

const SAMPLE_DOCTOR = {
  initials: 'JS', name: 'Dr. Jayesh Shah', spec: 'Diabetologist', city: 'Hyderabad',
  clinic: "Jayesh Shah's Clinic", cat: 'A+', score: 82, division: 'Life',
  qual: 'MBBS (MD unverified)', clinicFull: "Jayesh Shah's Clinic, PG Road, Secunderabad",
  interests: 'T2DM · SGLT2 · GLP-1 · Metabolic syndrome', channel: 'WhatsApp (after 7 PM)',
  mr: 'Ravi Kumar', birthday: '12 May', anniversary: '28 November',
  family: 'Spouse: Dr. Priya Shah · 2 children',
  lastVisit: '14 Apr', sow: '77%', sowSub: 'of ₹3.1L potential',
  dms: '₹1.86L', contentSent: 3, lastSent: 'Last: 8 Apr',
  aiTags: ['T2DM', 'SGLT2 Inhibitors', 'GLP-1 Therapy', 'Insulin Resistance', 'Metabolic Syndrome', 'DPP-4'],
  timeline: [
    { title: 'SGLT2 Trial Results shared via WhatsApp', sub: 'Opened · Read time: 4 min', date: '8 Apr 2026', color: 'var(--green)' },
    { title: 'MR Visit — discussed GLP-1 trial results', sub: 'In-clinic · Positive reception', date: '2 Apr 2026', color: 'var(--navy)' },
    { title: 'Metformin Outcomes paper shared', sub: 'Opened · Forwarded to colleague', date: '22 Mar 2026', color: 'var(--green)' },
    { title: 'Birthday wish sent (cake via FNP)', sub: 'Delivered · Doctor replied with thanks', date: '12 Mar 2026', color: 'var(--gold)' },
  ],
  dmsChart: [
    { month: 'Nov', value: 1.2 },
    { month: 'Dec', value: 1.4 },
    { month: 'Jan', value: 1.5 },
    { month: 'Feb', value: 1.6 },
    { month: 'Mar', value: 1.7 },
    { month: 'Apr', value: 1.86 },
  ],
};

// Map DoctorDirectory fields → Doctor360 display fields
function buildDocFromDirectory(d) {
  const firstName = d.name.replace('Dr. ', '').split(' ')[0];
  const lastName = d.name.replace('Dr. ', '').split(' ').slice(1).join(' ');
  const initials = (firstName[0] || '') + (lastName[0] || '');
  return {
    initials,
    name: d.name,
    spec: d.specialty,
    city: d.city,
    clinic: `${firstName} ${lastName}'s Clinic`,
    cat: d.category,
    score: d.score,
    division: 'Life',
    qual: 'MBBS · MD',
    clinicFull: `${firstName} ${lastName}'s Clinic, ${d.city}`,
    interests: d.specialty + ' · Clinical Research',
    channel: 'WhatsApp',
    mr: 'Field Rep',
    birthday: '12 May',
    anniversary: '28 November',
    family: 'Family information not available',
    lastVisit: '14 Apr',
    sow: d.sow + '%',
    sowSub: `of ₹${(d.dm_score * 35).toLocaleString('en-IN')} potential`,
    dms: '₹' + (d.dm_score * 0.022).toFixed(2) + 'L',
    contentSent: 3,
    lastSent: 'Last: 8 Apr',
    aiTags: [d.specialty, 'Evidence-Based Medicine', 'Clinical Research', 'Patient Care'],
    timeline: SAMPLE_DOCTOR.timeline,
    dmsChart: SAMPLE_DOCTOR.dmsChart,
  };
}

export default function Doctor360() {
  const { setCurrentTab, selectedDoctor } = useAppContext();
  const [activeTab, setActiveTab] = useState('overview');

  // Use selected doctor from directory, or fall back to sample
  const doc = selectedDoctor ? buildDocFromDirectory(selectedDoctor) : SAMPLE_DOCTOR;

  const scoreColor = doc.score >= 80 ? 'var(--green)' : doc.score >= 50 ? 'var(--amber)' : 'var(--red)';
  const maxDms = Math.max(...doc.dmsChart.map(d => d.value));

  const goBack = () => {
    setCurrentTab('doctors');
    window.location.hash = '#bu-head/doctors';
  };

  const tabs = [
    { key: 'overview', label: 'Overview' },
    { key: 'crm', label: 'Superman Intel' },
    { key: 'content', label: 'Content Sent' },
    { key: 'calendar', label: 'Engagement Calendar' },
  ];

  return (
    <div className={styles.container}>
      {/* Back button */}
      <div className={styles.backRow}>
        <button className={styles.backBtn} onClick={goBack}>
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8.5 2L3 6.5l5.5 4.5"/></svg>
          Back to Directory
        </button>
        <span className={styles.divisionBadge}>{doc.division} Division</span>
      </div>

      {/* Doctor Header */}
      <div className={styles.docHeader}>
        <div className={styles.dhAvatar}>{doc.initials}</div>
        <div className={styles.dhBody}>
          <div className={styles.dhLabel}>Pinnacle Doctor · 360° Profile</div>
          <div className={styles.dhName}>{doc.name}</div>
          <div className={styles.dhMeta}>
            <span>{doc.spec}</span>
            <span>{doc.city}</span>
            <span>{doc.clinic}</span>
          </div>
          <div className={styles.dhBadges}>
            <span className={`${styles.hBadge} ${styles.hbGold}`}>{doc.cat} Pinnacle</span>
            <span className={`${styles.hBadge} ${styles.hbGreen}`}>Well Engaged</span>
          </div>
        </div>
        <div className={styles.dhScore}>
          <div className={styles.scoreBig}>{doc.score}</div>
          <div className={styles.scoreLbl}>Engagement Score</div>
          <div className={styles.dhCtas}>
            <button className={styles.waBtn}>WhatsApp</button>
            <button className={styles.giftBtn}>Gift</button>
          </div>
        </div>
      </div>

      {/* KPIs */}
      <div className={styles.kpiRow}>
        <div className={`${styles.kpi} ${styles.kNavy}`}>
          <div className={styles.kpiLabel}>Last MR Visit</div>
          <div className={styles.kpiValue} style={{ fontSize: 20 }}>{doc.lastVisit}</div>
          <div className={styles.kpiSub}>Regular cadence</div>
        </div>
        <div className={`${styles.kpi} ${styles.kGold}`}>
          <div className={styles.kpiLabel}>SOW</div>
          <div className={styles.kpiValue}>{doc.sow}</div>
          <div className={styles.kpiSub}>{doc.sowSub}</div>
        </div>
        <div className={`${styles.kpi} ${styles.kGreen}`}>
          <div className={styles.kpiLabel}>DMS This Month</div>
          <div className={styles.kpiValue}>{doc.dms}</div>
          <div className={styles.kpiSub} style={{ color: 'var(--green)' }}>↑ Growing</div>
        </div>
        <div className={`${styles.kpi} ${styles.kTeal}`}>
          <div className={styles.kpiLabel}>Content Sent</div>
          <div className={styles.kpiValue}>{doc.contentSent}</div>
          <div className={styles.kpiSub}>{doc.lastSent}</div>
        </div>
      </div>

      {/* Tabs */}
      <div className={styles.tabBar}>
        {tabs.map(t => (
          <button
            key={t.key}
            className={`${styles.tab360} ${activeTab === t.key ? styles.tab360Active : ''}`}
            onClick={() => setActiveTab(t.key)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className={styles.overviewGrid}>
          {/* Quick Profile */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Quick Profile</div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>Qualification</div><div className={styles.infoValue}>{doc.qual}</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>Clinic</div><div className={styles.infoValue}>{doc.clinicFull}</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>Clinical Interests</div><div className={styles.infoValue}>{doc.interests}</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>Preferred Channel</div><div className={styles.infoValue}>{doc.channel}</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>MR Name</div><div className={styles.infoValue}>{doc.mr}</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>Pinnacle Division</div><div className={styles.infoValue}>{doc.division}</div></div>
          </div>

          {/* AI Interest Profile */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>
              AI Interest Profile <span className={styles.aiBadge}>AI</span>
            </div>
            <div className={styles.tagList}>
              {doc.aiTags.map(tag => (
                <span key={tag} className={styles.interestTag}>{tag}</span>
              ))}
            </div>
            <div className={styles.tagBasis}>Based on content opens and CRM data</div>
          </div>

          {/* Personal Info & Occasions */}
          <div className={`${styles.card} ${styles.cardFull}`}>
            <div className={styles.cardTitle}>Personal Information & Occasions</div>
            <div className={styles.personalRow}>
              <div className={styles.personalIcon} style={{ background: 'linear-gradient(135deg, #FEF3C7, #FDE68A)' }}>🎂</div>
              <div className={styles.personalInfo}>
                <div className={styles.personalLabel}>Birthday</div>
                <div className={styles.personalValue}>{doc.birthday} <span className={styles.countdownBadge}>8 days</span></div>
              </div>
              <div className={styles.personalCtas}>
                <button className={styles.waBtn}>Wish</button>
                <button className={styles.giftBtn}>🎂 Cake</button>
              </div>
            </div>
            <div className={styles.personalRow}>
              <div className={styles.personalIcon} style={{ background: 'linear-gradient(135deg, #FCE7F3, #FBCFE8)' }}>💍</div>
              <div className={styles.personalInfo}>
                <div className={styles.personalLabel}>Anniversary</div>
                <div className={styles.personalValue}>{doc.anniversary}</div>
              </div>
              <div className={styles.personalCtas}>
                <button className={styles.waBtn}>Wish</button>
                <button className={styles.giftBtn}>🌹 Flowers</button>
              </div>
            </div>
            <div className={styles.personalRow}>
              <div className={styles.personalIcon} style={{ background: 'linear-gradient(135deg, #D1FAE5, #A7F3D0)' }}>👨‍👩‍👧</div>
              <div className={styles.personalInfo}>
                <div className={styles.personalLabel}>Family</div>
                <div className={styles.personalValue}>{doc.family}</div>
              </div>
            </div>
            <div className={styles.personalRow}>
              <div className={styles.personalIcon} style={{ background: 'linear-gradient(135deg, #FEE2E2, #FECACA)' }}>📱</div>
              <div className={styles.personalInfo}>
                <div className={styles.personalLabel}>Preferred Channel</div>
                <div className={styles.personalValue}>{doc.channel}</div>
              </div>
              <div className={styles.personalCtas}>
                <button className={styles.waBtn}>Message</button>
              </div>
            </div>
          </div>

          {/* DMS Trend */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>DMS Trend (6 months)</div>
            <div className={styles.chartArea}>
              {doc.dmsChart.map((d, i) => (
                <div key={i} className={styles.chartCol}>
                  <div
                    className={styles.chartBar}
                    style={{
                      height: `${(d.value / maxDms) * 70}px`,
                      background: `linear-gradient(180deg, var(--navy), var(--navy3))`,
                    }}
                  />
                  <div className={styles.chartValue}>₹{d.value}L</div>
                  <div className={styles.chartMonth}>{d.month}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Engagement Timeline */}
          <div className={styles.card}>
            <div className={styles.cardTitle}>Engagement Timeline</div>
            {doc.timeline.map((item, i) => (
              <div key={i} className={styles.tlItem}>
                <div className={styles.tlDot} style={{ background: item.color }} />
                <div>
                  <div className={styles.tlTitle}>{item.title}</div>
                  <div className={styles.tlSub}>{item.sub}</div>
                  <div className={styles.tlDate}>{item.date}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Superman Intel Tab */}
      {activeTab === 'crm' && (
        <div className={styles.overviewGrid}>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Superman Intel — CRM Data</div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>MR Name</div><div className={styles.infoValue} style={{ fontWeight: 700 }}>Ramesh Nair</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>Last MR Visit</div><div className={styles.infoValue}>14 Apr 2026</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>Visits L3M</div><div className={styles.infoValue}>28 visits</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>eDetailing Sessions</div><div className={styles.infoValue}>16 · avg 5.6 min</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>DM (Monthly Potential)</div><div className={styles.infoValue} style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700 }}>₹3,10,000</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>DMS (Last Month)</div><div className={styles.infoValue} style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700 }}>₹2,20,000</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>DMS (This Month)</div><div className={styles.infoValue} style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, color: 'var(--green)' }}>₹2,40,000 ↑</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>SOW</div><div className={styles.infoValue} style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 700, color: 'var(--amber)' }}>77.4%</div></div>
            <div className={styles.infoRow}><div className={styles.infoLabel}>Products</div><div className={styles.infoValue} style={{ fontSize: 11 }}>DYNADUO · DYNAGLIPT · Glykind · SGLT-D</div></div>
          </div>

          <div className={styles.card}>
            <div className={styles.cardTitle}>DMS Trend — Last 7 Months</div>
            <div className={styles.chartArea}>
              {[
                { month: 'Oct', value: 2.2 },
                { month: 'Nov', value: 2.0 },
                { month: 'Dec', value: 1.9 },
                { month: 'Jan', value: 1.8 },
                { month: 'Feb', value: 1.7 },
                { month: 'Mar', value: 1.7 },
                { month: 'Apr', value: 2.4 },
              ].map((d, i) => (
                <div key={i} className={styles.chartCol}>
                  <div
                    className={styles.chartBar}
                    style={{
                      height: `${(d.value / 2.4) * 70}px`,
                      background: i === 6 ? 'linear-gradient(180deg, #D4A843, #D4A843)' : 'linear-gradient(180deg, var(--navy), var(--navy3))',
                    }}
                  />
                  <div className={styles.chartValue}>₹{d.value}L</div>
                  <div className={styles.chartMonth}>{d.month}</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid var(--border)', fontSize: 11, color: 'var(--text3)' }}>
              6-month growth: <strong style={{ color: 'var(--green)' }}>+33%</strong> · SOW gap: <strong style={{ color: 'var(--amber)' }}>₹70K/month</strong>
            </div>
          </div>
        </div>
      )}

      {/* Content Sent Tab */}
      {activeTab === 'content' && (
        <div className={styles.overviewGrid}>
          <div className={styles.card}>
            <div className={styles.cardTitle}>Content Sent History</div>
            {[
              { title: 'SGLT2 Inhibitors and CV Outcomes in T2DM — Meta-Analysis', channel: 'WhatsApp', status: 'Opened · 12 min', date: '8 Apr 2026', color: 'var(--blue)' },
              { title: 'GLP-1 Receptor Agonists: Real-World Outcomes in South Asian Populations', channel: 'Email', status: 'Discussed at MR visit', date: '22 Mar 2026', color: 'var(--green)' },
              { title: 'Insulin Resistance in Metabolic Syndrome: 2025 Consensus', channel: 'WhatsApp', status: 'No response tracked', date: '5 Mar 2026', color: 'var(--text4)' },
            ].map((item, i) => (
              <div key={i} className={styles.tlItem}>
                <div className={styles.tlDot} style={{ background: item.color }} />
                <div>
                  <div className={styles.tlTitle}>{item.title}</div>
                  <div className={styles.tlSub}>{item.channel} · {item.status}</div>
                  <div className={styles.tlDate}>{item.date}</div>
                </div>
              </div>
            ))}
          </div>

          <div className={styles.card}>
            <div className={styles.cardTitle}>Engagement Performance</div>
            {[
              { label: '💬 WhatsApp', value: 85, color: 'var(--green)' },
              { label: '✉️ Email', value: 50, color: 'var(--amber)' },
              { label: '📞 MR Follow-up', value: 100, color: 'var(--blue)' },
            ].map((item, i) => (
              <div key={i} style={{ marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                  <span style={{ fontSize: 12 }}>{item.label}</span>
                  <span style={{ fontSize: 12, fontWeight: 700, color: item.color }}>{item.value}%</span>
                </div>
                <div style={{ height: 6, background: 'var(--border)', borderRadius: 4, overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${item.value}%`, background: item.color, borderRadius: 4 }} />
                </div>
              </div>
            ))}

            <div style={{ marginTop: 14, paddingTop: 12, borderTop: '1px solid var(--border)' }}>
              <div className={styles.cardTitle} style={{ marginBottom: 8 }}>
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none" style={{ marginRight: 4 }}>
                  <path d="M6 .4l.8 2.5H9.6L7.4 4.5l.8 2.5L6 5.6l-2.2 1.4.8-2.5L2.4 2.9H5.2L6 .4z" fill="#7C3AED" opacity=".8"/>
                </svg>
                AI Insight
              </div>
              <div style={{ background: 'var(--green-bg)', border: '1px solid var(--green-bd)', borderRadius: 8, padding: 10, fontSize: 12, color: 'var(--green)' }}>
                No content fatigue. Last 3 sends all opened. Recommended send frequency: <strong>every 10–14 days</strong>.
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Engagement Calendar Tab */}
      {activeTab === 'calendar' && (
        <div className={styles.card}>
          <div className={styles.cardTitle} style={{ marginBottom: 20 }}>Engagement Calendar</div>
          <div style={{ textAlign: 'center', padding: '40px 20px' }}>
            <div style={{ fontSize: 48, marginBottom: 16 }}>📅</div>
            <div style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 16, fontWeight: 700, color: 'var(--navy)', marginBottom: 8 }}>Engagement Calendar</div>
            <div style={{ fontSize: 13, color: 'var(--text3)', marginBottom: 20 }}>
              Coming soon — Interactive calendar view with logged visits, engagements, and upcoming events.
            </div>
            <button style={{
              background: 'linear-gradient(135deg, var(--gold2), var(--gold))',
              color: 'var(--navy)',
              border: 'none',
              padding: '8px 14px',
              borderRadius: 9,
              fontSize: 12,
              fontWeight: 800,
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 6,
            }}>
              <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><line x1="6.5" y1="2" x2="6.5" y2="11"/><line x1="2" y1="6.5" x2="11" y2="6.5"/></svg>
              Log Visit / Event
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
