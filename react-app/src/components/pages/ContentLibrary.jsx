/**
 * ContentLibrary — Medical Affairs Content Management
 *
 * MA Role:  Add Content button, Pending Review / Approve / Reject workflow,
 *           MA-specific KPIs (Total, Pending, Approved, AI-generated)
 *
 * PMT Role: Browse approved content, share with doctors
 *           PMT-specific KPIs (Total, Approved, Shared, Trending)
 */
import React, { useState, useMemo } from 'react';
import { useAuth } from '../../hooks/useAuth';
import { useContent } from '../../hooks/useContent';
import { useAppContext } from '../../hooks/useAppContext';
import AddContentWizard from './AddContentWizard';
import ShareModal from './ShareModal';
import styles from './ContentLibrary.module.css';

/* ── Static sample data ─────────────────────────────────────────────────── */
const SAMPLE_PAPERS = [
  {
    id: 'cl-001',
    status: 'approved',
    source: 'pubmed',
    title: 'SGLT2 Inhibitors and Cardiovascular Outcomes in Heart Failure: EMPEROR and DAPA-HF 3-Year Follow-Up',
    journal: 'New England Journal of Medicine',
    year: '2024',
    authors: 'Packer M, Anker SD, Butler J, Filippatos G, et al.',
    pmid: '38291234',
    pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/38291234/',
    specialty: 'Cardiology',
    therapy_area: 'Heart Failure',
    sub_category: 'Clinical Trial / RCT',
    tags: ['SGLT2', 'Heart Failure', 'Empagliflozin', 'HFrEF', 'ESC 2025'],
    summary: 'Three-year follow-up data from EMPEROR-Reduced and DAPA-HF confirm SGLT2 inhibitors reduce hospitalisation for heart failure by 30% and CV mortality by 18% in both HFrEF and HFpEF patients, regardless of diabetes status.',
    reviewer: 'Dr. Prashant Agarwal',
    date: '2025-04-22',
  },
  {
    id: 'cl-002',
    status: 'approved',
    source: 'pubmed',
    title: 'GLP-1 Receptor Agonists in Type 2 Diabetes: 2025 Real-World Evidence Update',
    journal: 'Diabetes Care (ADA)',
    year: '2025',
    authors: 'Nauck MA, Quast DR, Wefers J, Meier JJ, et al.',
    pmid: '39102847',
    pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/39102847/',
    specialty: 'Diabetology',
    therapy_area: 'GLP-1 Therapy',
    sub_category: 'Meta-Analysis / Systematic Review',
    tags: ['GLP-1', 'Semaglutide', 'T2DM', 'Cardiovascular', 'Indian Population'],
    summary: 'A landmark 2025 meta-analysis of 34 RCTs (n=87,420) confirms GLP-1 receptor agonists deliver superior glycaemic control alongside significant cardiovascular and renal protection benefits.',
    reviewer: 'Dr. Prashant Agarwal',
    date: '2025-05-15',
  },
  {
    id: 'cl-003',
    status: 'pending',
    source: 'ai_agent',
    title: 'Inositol vs Metformin in PCOS: 2025 Systematic Review and Indian Cohort Data',
    journal: 'Fertility and Sterility',
    year: '2025',
    authors: 'Unfer V, Grillone R, Laganà AS, Bizzarri M, et al.',
    pmid: '38712089',
    pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/38712089/',
    specialty: 'Gynaecology',
    therapy_area: 'PCOS',
    sub_category: 'Meta-Analysis / Systematic Review',
    tags: ['PCOS', 'Inositol', 'Metformin', 'Fertility', 'Indian Population'],
    summary: 'A 2025 systematic review of 22 RCTs (n=3,180) demonstrates myo-inositol achieves comparable insulin sensitisation to metformin with significantly fewer GI adverse effects (12% vs 34%).',
    reviewer: null,
    date: '2025-05-28',
  },
  {
    id: 'cl-004',
    status: 'pending',
    source: 'ai_agent',
    title: 'Paediatric Vaccination Schedule Updates 2024-25: India-Specific Recommendations',
    journal: 'Indian Paediatrics',
    year: '2025',
    authors: 'IAP Expert Panel, Vashishtha VM, Choudhury P, et al.',
    pmid: '39021847',
    pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/39021847/',
    specialty: 'Paediatrics',
    therapy_area: 'Immunisation',
    sub_category: 'Expert Opinion / Guidelines',
    tags: ['Vaccination', 'IAP', 'Paediatrics', 'India 2025'],
    summary: 'Updated 2025 IAP vaccination schedule with new additions including MenACWY, PCV-13 boosters, and rotavirus catch-up guidance for Indian children.',
    reviewer: null,
    date: '2025-05-20',
  },
  {
    id: 'cl-005',
    status: 'approved',
    source: 'upload',
    title: 'Dupilumab for Moderate-to-Severe Atopic Dermatitis: Long-Term Safety and Efficacy Data',
    journal: 'JAMA Dermatology',
    year: '2024',
    authors: 'Simpson EL, Bieber T, Guttman-Yassky E, et al.',
    pmid: '37891234',
    pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/37891234/',
    specialty: 'Dermatology',
    therapy_area: 'Acne & Skin',
    sub_category: 'Clinical Trial / RCT',
    tags: ['Dupilumab', 'Atopic Dermatitis', 'Biologics', 'Long-term Safety'],
    summary: '52-week extension study confirms dupilumab maintains 75% EASI improvement with excellent safety profile across all age groups including adolescents.',
    reviewer: 'Dr. Prashant Agarwal',
    date: '2024-11-10',
  },
  {
    id: 'cl-006',
    status: 'rejected',
    source: 'ai_agent',
    title: 'Tirzepatide in Obesity Without Diabetes: SURMOUNT-1 Trial',
    journal: 'New England Journal of Medicine',
    year: '2024',
    authors: 'Jastreboff AM, Aronne LJ, Ahmad NN, et al.',
    pmid: '38234567',
    pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/38234567/',
    specialty: 'Endocrinology',
    therapy_area: 'GLP-1 Therapy',
    sub_category: 'Clinical Trial / RCT',
    tags: ['Tirzepatide', 'Obesity', 'SURMOUNT-1', 'Weight Loss'],
    summary: 'Tirzepatide achieves up to 22.5% body weight reduction at 72 weeks in adults with obesity but without diabetes.',
    reviewer: 'Dr. Prashant Agarwal',
    reject_reason: 'Not currently in Mankind portfolio scope. Re-review in Q3 2025.',
    date: '2024-12-05',
  },
];

const SPECIALTIES  = ['All Specialties', 'Cardiology', 'Diabetology', 'Gynaecology', 'Endocrinology', 'Paediatrics', 'Dermatology'];
const THERAPY_AREAS = ['All Therapy Areas', 'Heart Failure', 'GLP-1 Therapy', 'PCOS', 'Immunisation', 'Acne & Skin', 'Type 2 Diabetes'];
const SOURCES = ['All Sources', 'pubmed', 'upload', 'ai_agent', 'link'];
const SOURCE_LABELS = { pubmed: 'PubMed', upload: 'MA Upload', ai_agent: 'AI Generated', link: 'Web Link' };

/* ── Source badge ────────────────────────────────────────────────────────── */
function SourceBadge({ source }) {
  const map = {
    pubmed:   { bg: 'var(--blue-bg)',   color: 'var(--blue)',   label: 'PubMed' },
    upload:   { bg: 'var(--purple-bg)', color: 'var(--purple)', label: 'MA Upload' },
    ai_agent: { bg: '#F0FDF4',          color: 'var(--green)',  label: '🤖 AI Generated' },
    link:     { bg: 'var(--amber-bg)',  color: 'var(--amber)',  label: 'Web Link' },
  };
  const s = map[source] || map.link;
  return (
    <span className={styles.sourceBadge} style={{ background: s.bg, color: s.color }}>
      {s.label}
    </span>
  );
}

/* ── Status badge ────────────────────────────────────────────────────────── */
function StatusBadge({ status }) {
  const map = {
    approved: { bg: 'var(--green-bg)',   color: 'var(--green)',   label: '✅ Approved' },
    pending:  { bg: 'var(--amber-bg)',   color: 'var(--amber)',   label: '⏳ Pending Review' },
    rejected: { bg: 'var(--red-bg)',     color: 'var(--red)',     label: '✗ Rejected' },
  };
  const s = map[status] || map.pending;
  return (
    <span className={styles.statusBadge} style={{ background: s.bg, color: s.color }}>
      {s.label}
    </span>
  );
}

/* ── Paper card ──────────────────────────────────────────────────────────── */
function PaperCard({ paper, isMA, onApprove, onReject, onShare }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className={`${styles.paperCard} ${paper.status === 'pending' ? styles.paperCardPending : ''}`}>
      {/* Card header row */}
      <div className={styles.pcHeader}>
        <div className={styles.pcMeta}>
          <SourceBadge source={paper.source} />
          {isMA && <StatusBadge status={paper.status} />}
          <span className={styles.pcDate}>{paper.date}</span>
        </div>
        <div className={styles.pcTags}>
          {(paper.tags || []).slice(0, 3).map(t => (
            <span key={t} className={styles.pcTag}>{t}</span>
          ))}
        </div>
      </div>

      {/* Title */}
      <div className={styles.pcTitle}>{paper.title}</div>

      {/* Meta */}
      <div className={styles.pcJournal}>
        <span>📰 {paper.journal}{paper.year ? `, ${paper.year}` : ''}</span>
        <span className={styles.pcDot}>·</span>
        <span>👤 {paper.authors}</span>
        {paper.pmid && (
          <>
            <span className={styles.pcDot}>·</span>
            <a href={paper.pubmed_link || `https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`}
               target="_blank" rel="noopener noreferrer" className={styles.pcPmid}>
              📖 PMID {paper.pmid}
            </a>
          </>
        )}
      </div>

      {/* Speciality pills */}
      <div className={styles.pcSpecRow}>
        <span className={styles.pcSpecBadge}>{paper.specialty}</span>
        <span className={styles.pcSpecBadge} style={{ background: 'var(--purple-bg)', color: 'var(--purple)' }}>
          {paper.therapy_area}
        </span>
        <span className={styles.pcSubCat}>{paper.sub_category}</span>
      </div>

      {/* Summary (expandable) */}
      <div className={`${styles.pcSummary} ${expanded ? styles.pcSummaryExpanded : ''}`}>
        {paper.summary}
      </div>
      {paper.summary?.length > 120 && (
        <button className={styles.expandBtn} onClick={() => setExpanded(e => !e)}>
          {expanded ? '▲ Less' : '▼ Read more'}
        </button>
      )}

      {/* Reject reason (if rejected) */}
      {paper.status === 'rejected' && paper.reject_reason && (
        <div className={styles.rejectNote}>
          ✗ Rejection note: {paper.reject_reason}
        </div>
      )}

      {/* Action buttons */}
      <div className={styles.pcActions}>
        {isMA && paper.status === 'pending' && (
          <>
            <button className={styles.approveBtn} onClick={() => onApprove(paper.id)}>
              ✅ Approve
            </button>
            <button className={styles.rejectBtn} onClick={() => onReject(paper.id)}>
              ✗ Reject
            </button>
          </>
        )}
        {isMA && paper.status === 'approved' && (
          <span className={styles.approvedNote}>✅ Approved by {paper.reviewer}</span>
        )}
        {!isMA && paper.status === 'approved' && (
          <button className={styles.shareBtn} onClick={() => onShare(paper)}>
            📱 Share with Doctor
          </button>
        )}
      </div>
    </div>
  );
}

/* ── Main Component ──────────────────────────────────────────────────────── */
export default function ContentLibrary() {
  const { isMA } = useAuth();
  const { addNotification } = useAppContext();

  // Local state for papers (starts with sample data + any API papers)
  const [papers, setPapers] = useState(SAMPLE_PAPERS);
  const [showWizard, setShowWizard] = useState(false);
  const [shareTarget, setShareTarget] = useState(null);  // paper being shared

  // Filter state
  const [search,      setSearch]     = useState('');
  const [specialty,   setSpecialty]  = useState('All Specialties');
  const [therapyArea, setTherapyArea] = useState('All Therapy Areas');
  const [sourceFilter, setSourceFilter] = useState('All Sources');
  const [activeTab,   setActiveTab]  = useState('all');

  // Computed KPIs
  const total    = papers.length;
  const pending  = papers.filter(p => p.status === 'pending').length;
  const approved = papers.filter(p => p.status === 'approved').length;
  const aiGen    = papers.filter(p => p.source === 'ai_agent').length;

  // Tabs config per role
  const maTabs  = ['all', 'pending', 'approved', 'rejected'];
  const pmtTabs = ['all', 'Cardiology', 'Diabetology', 'Gynaecology', 'Paediatrics'];

  // Filtered papers
  const filtered = useMemo(() => {
    let list = [...papers];

    // Tab filter
    if (activeTab !== 'all') {
      if (isMA) {
        list = list.filter(p => p.status === activeTab);
      } else {
        list = list.filter(p => p.specialty === activeTab);
      }
    }

    // For PMT, only show approved
    if (!isMA) list = list.filter(p => p.status === 'approved');

    // Search
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(p =>
        p.title.toLowerCase().includes(q) ||
        p.authors?.toLowerCase().includes(q) ||
        p.journal?.toLowerCase().includes(q) ||
        (p.tags || []).some(t => t.toLowerCase().includes(q))
      );
    }

    // Specialty filter
    if (specialty !== 'All Specialties') {
      list = list.filter(p => p.specialty === specialty);
    }

    // Therapy area filter
    if (therapyArea !== 'All Therapy Areas') {
      list = list.filter(p => p.therapy_area === therapyArea);
    }

    // Source filter
    if (sourceFilter !== 'All Sources') {
      list = list.filter(p => p.source === sourceFilter);
    }

    return list;
  }, [papers, activeTab, search, specialty, therapyArea, sourceFilter, isMA]);

  const hasFilters = search || specialty !== 'All Specialties' || therapyArea !== 'All Therapy Areas' || sourceFilter !== 'All Sources';

  /* ── Actions ── */
  function handleApprove(id) {
    setPapers(prev => prev.map(p => p.id === id ? { ...p, status: 'approved', reviewer: 'Dr. Prashant Agarwal' } : p));
    addNotification('Paper approved and now visible to PMT team.', 'success');
  }

  function handleReject(id) {
    const reason = window.prompt('Rejection reason (optional):') ?? '';
    setPapers(prev => prev.map(p => p.id === id ? { ...p, status: 'rejected', reviewer: 'Dr. Prashant Agarwal', reject_reason: reason || 'Rejected by MA.' } : p));
    addNotification('Paper rejected.', 'info');
  }

  /* Opens the 2-step Share Doctor Picker modal */
  function handleShare(paper) {
    setShareTarget(paper);
  }

  /* Called when the modal successfully sends */
  function handleShared(doctors, channel, message, paper) {
    const names = doctors.map(d => d.name.replace('Dr. ', '')).join(', ');
    const ch = channel === 'both' ? 'WhatsApp & Email' : channel === 'whatsapp' ? 'WhatsApp' : 'Email';
    addNotification(`"${paper.title.slice(0, 36)}…" shared with ${doctors.length} doctor${doctors.length !== 1 ? 's' : ''} via ${ch}.`, 'success');
  }

  function handleContentAdded(newCard) {
    setPapers(prev => [{ ...newCard, status: newCard.status || 'approved' }, ...prev]);
    addNotification('Content added to library and available to PMT!', 'success');
  }

  function clearFilters() {
    setSearch(''); setSpecialty('All Specialties'); setTherapyArea('All Therapy Areas'); setSourceFilter('All Sources');
  }

  return (
    <div className={styles.container}>

      {/* ── MA Banner ── */}
      {isMA && (
        <div className={styles.maBanner}>
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="var(--blue)" strokeWidth="1.5" strokeLinecap="round">
            <circle cx="9" cy="9" r="7.5"/>
            <path d="M6 9.5l2 2 4-4"/>
          </svg>
          <div>
            <div className={styles.maBannerTitle}>Medical Affairs View</div>
            <div className={styles.maBannerSub}>Review AI-generated papers, edit summaries, approve or reject for PMT sharing</div>
          </div>
        </div>
      )}

      {/* ── Header ── */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Content Library</h1>
          <p className={styles.subtitle}>
            {isMA
              ? `${total} articles · ${pending} pending review · ${approved} approved`
              : `${approved} approved articles available`}
          </p>
        </div>
        {isMA && (
          <button className={styles.addBtn} onClick={() => setShowWizard(true)}>
            <span className={styles.addBtnPlus}>＋</span>
            Add Content
          </button>
        )}
      </div>

      {/* ── KPI Row ── */}
      <div className={styles.kpiRow}>
        {isMA ? (
          <>
            <div className={`${styles.kpi} ${styles.kpiNavy}`}>
              <div className={styles.kpiLabel}>Total Articles</div>
              <div className={styles.kpiValue}>{total}</div>
              <div className={styles.kpiSub}>In library</div>
            </div>
            <div className={`${styles.kpi} ${styles.kpiAmber}`}>
              <div className={styles.kpiLabel}>Pending Review</div>
              <div className={styles.kpiValue} style={{ color: 'var(--amber)' }}>{pending}</div>
              <div className={styles.kpiSub}>Awaiting your review</div>
            </div>
            <div className={`${styles.kpi} ${styles.kpiGreen}`}>
              <div className={styles.kpiLabel}>Approved</div>
              <div className={styles.kpiValue} style={{ color: 'var(--green)' }}>{approved}</div>
              <div className={styles.kpiSub}>Visible to PMT</div>
            </div>
            <div className={`${styles.kpi} ${styles.kpiTeal}`}>
              <div className={styles.kpiLabel}>AI Generated</div>
              <div className={styles.kpiValue}>{aiGen}</div>
              <div className={styles.kpiSub}>From Research Pipeline</div>
            </div>
          </>
        ) : (
          <>
            <div className={`${styles.kpi} ${styles.kpiNavy}`}>
              <div className={styles.kpiLabel}>Available</div>
              <div className={styles.kpiValue}>{approved}</div>
              <div className={styles.kpiSub}>Approved by MA</div>
            </div>
            <div className={`${styles.kpi} ${styles.kpiGreen}`}>
              <div className={styles.kpiLabel}>Shared</div>
              <div className={styles.kpiValue}>18</div>
              <div className={styles.kpiSub}>Sent to doctors</div>
            </div>
            <div className={`${styles.kpi} ${styles.kpiGold}`}>
              <div className={styles.kpiLabel}>Trending</div>
              <div className={styles.kpiValue}>4</div>
              <div className={styles.kpiSub}>High engagement this week</div>
            </div>
            <div className={`${styles.kpi} ${styles.kpiTeal}`}>
              <div className={styles.kpiLabel}>Specialties</div>
              <div className={styles.kpiValue}>6</div>
              <div className={styles.kpiSub}>Covered this month</div>
            </div>
          </>
        )}
      </div>

      {/* ── Tabs ── */}
      <div className={styles.tabRow}>
        <div className={styles.tabs}>
          {(isMA ? maTabs : pmtTabs).map(tab => (
            <button
              key={tab}
              className={`${styles.tab} ${activeTab === tab ? styles.tabActive : ''}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab === 'all' ? 'All' : tab.charAt(0).toUpperCase() + tab.slice(1)}
              {isMA && tab === 'pending' && pending > 0 && (
                <span className={styles.tabBadge}>{pending}</span>
              )}
            </button>
          ))}
        </div>

        {/* View toggle placeholder */}
        <div className={styles.viewToggle}>
          <button className={`${styles.vBtn} ${styles.vBtnActive}`} title="Grid">⊞</button>
          <button className={styles.vBtn} title="List">≡</button>
        </div>
      </div>

      {/* ── Filters ── */}
      <div className={styles.filters}>
        <div className={styles.searchBox}>
          <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="#9CA3AF" strokeWidth="1.6" strokeLinecap="round">
            <circle cx="5" cy="5" r="4"/><line x1="8.5" y1="8.5" x2="12" y2="12"/>
          </svg>
          <input
            className={styles.searchInput}
            type="text"
            placeholder="Search title, journal, author…"
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>

        <select className={styles.filterSelect} value={specialty} onChange={e => setSpecialty(e.target.value)}>
          {SPECIALTIES.map(s => <option key={s}>{s}</option>)}
        </select>

        <select className={styles.filterSelect} value={therapyArea} onChange={e => setTherapyArea(e.target.value)}>
          {THERAPY_AREAS.map(t => <option key={t}>{t}</option>)}
        </select>

        {isMA && (
          <select className={styles.filterSelect} value={sourceFilter} onChange={e => setSourceFilter(e.target.value)}>
            {SOURCES.map(s => <option key={s} value={s}>{s === 'All Sources' ? 'All Sources' : SOURCE_LABELS[s]}</option>)}
          </select>
        )}

        {hasFilters && (
          <button className={styles.clearBtn} onClick={clearFilters}>✕ Clear</button>
        )}
      </div>

      {/* ── Count ── */}
      <div className={styles.countRow}>
        <span className={styles.countText}>
          {filtered.length} of {isMA ? total : approved} articles
          {hasFilters && <span className={styles.activeFilter}> · Filtered</span>}
        </span>
      </div>

      {/* ── Papers Grid ── */}
      {filtered.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyIcon}>📄</div>
          <p className={styles.emptyText}>No articles match your filters.</p>
          {hasFilters && <button className={styles.clearBtn} onClick={clearFilters}>Clear filters</button>}
        </div>
      ) : (
        <div className={styles.papersGrid}>
          {filtered.map(p => (
            <PaperCard
              key={p.id}
              paper={p}
              isMA={isMA}
              onApprove={handleApprove}
              onReject={handleReject}
              onShare={handleShare}
            />
          ))}
        </div>
      )}

      {/* ── Add Content Wizard (MA only) ── */}
      {showWizard && (
        <AddContentWizard
          onClose={() => setShowWizard(false)}
          onAdded={handleContentAdded}
        />
      )}

      {/* ── Share Doctor Picker (PMT — approved papers) ── */}
      {shareTarget && (
        <ShareModal
          paper={shareTarget}
          onClose={() => setShareTarget(null)}
          onSent={handleShared}
        />
      )}
    </div>
  );
}
