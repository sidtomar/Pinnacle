/**
 * ShareModal — 2-step Share Doctor Picker
 *
 * Step 1: Select Doctors
 *   - "AI Recommended" tab: up to 6 doctors matched by paper specialty/therapy area
 *   - "All Doctors" tab: full table with checkbox multi-select + search + specialty filter
 *
 * Step 2: Review & Send
 *   - Recipient pills, channel selector (WhatsApp / Email / Both),
 *     AI-drafted message preview (editable), Send action
 *
 * Ref: PinnacleIQ - Responsive.html › share-modal, openSend(), buildAIRecs()
 */
import React, { useState, useMemo } from 'react';
import styles from './ShareModal.module.css';

/* ── Demo doctor data (mirrors design HTML DOCTORS array) ─────────────────── */
const DOCTORS = [
  { id: 1, name: 'Dr. Jayesh Shah',      init: 'JS', spec: 'Diabetology',    city: 'Hyderabad',    score: 82, last: 'Today',    cat: 'A+', interests: ['T2DM', 'SGLT2', 'GLP-1', 'Metabolic syndrome'] },
  { id: 2, name: 'Dr. Priya Nair',       init: 'PN', spec: 'Gynaecology',    city: 'Bangalore',    score: 81, last: '2 May',    cat: 'A+', interests: ['PCOS', 'Fertility', 'Hormonal disorders'] },
  { id: 3, name: 'Dr. Kavita Joshi',     init: 'KJ', spec: 'Gynaecology',    city: 'Pune',         score: 76, last: '28 Apr',   cat: 'A',  interests: ['PCOS', 'Endometriosis', 'Inositol'] },
  { id: 4, name: 'Dr. Madhukar Rai',     init: 'MR', spec: 'Endocrinology',  city: 'Varanasi',     score: 76, last: '25 Apr',   cat: 'A+', interests: ['T2DM', 'Thyroid', 'Insulin resistance'] },
  { id: 5, name: 'Dr. Arvind Patel',     init: 'AP', spec: 'Paediatrics',    city: 'Ahmedabad',    score: 79, last: '3 May',    cat: 'A+', interests: ['Vaccination', 'Growth disorders', 'Neonatal care'] },
  { id: 6, name: 'Dr. Giridhari Jena',   init: 'GJ', spec: 'Cardiology',     city: 'Bhubaneswar',  score: 44, last: '22 Mar',   cat: 'A',  interests: ['Heart Failure', 'SGLT2', 'Hypertension'] },
  { id: 7, name: 'Dr. S.K. Singh',       init: 'SS', spec: 'Endocrinology',  city: 'Varanasi',     score: 18, last: 'Never',   cat: 'A+', interests: ['T2DM', 'Obesity', 'SGLT2'] },
  { id: 8, name: 'Dr. Deepa Krishnan',   init: 'DK', spec: 'Gynaecology',    city: 'Kolkata',      score: 38, last: '15 Mar',   cat: 'A',  interests: ['PCOS', 'Menopause', 'Hormonal therapy'] },
  { id: 9, name: 'Dr. Rohit Bhansali',   init: 'RB', spec: 'Dermatology',    city: 'Mumbai',       score: 71, last: '1 May',    cat: 'A',  interests: ['Atopic Dermatitis', 'Biologics', 'Acne'] },
  { id: 10, name: 'Dr. Ananya Verma',    init: 'AV', spec: 'Cardiology',     city: 'Chennai',      score: 88, last: 'Today',    cat: 'A+', interests: ['Heart Failure', 'HFrEF', 'SGLT2', 'ESC Guidelines'] },
];

const SPECIALTIES = ['All Specialties', 'Diabetology', 'Cardiology', 'Gynaecology', 'Endocrinology', 'Paediatrics', 'Dermatology'];

const CHANNELS = [
  { id: 'whatsapp', icon: '💬', label: 'WhatsApp' },
  { id: 'email',    icon: '✉️', label: 'Email' },
  { id: 'both',     icon: '📱', label: 'Both' },
];

/* ── Helpers ────────────────────────────────────────────────────────────────── */
function scoreColor(s) {
  return s >= 80 ? 'var(--green)' : s >= 50 ? 'var(--amber)' : 'var(--red)';
}

function ScoreRing({ score }) {
  const r = 11, circ = 2 * Math.PI * r;
  const c = scoreColor(score);
  return (
    <svg width="28" height="28" viewBox="0 0 28 28" style={{ flexShrink: 0 }}>
      <circle cx="14" cy="14" r={r} fill="none" stroke="var(--surface3)" strokeWidth="3" />
      <circle cx="14" cy="14" r={r} fill="none" stroke={c} strokeWidth="3"
        strokeDasharray={`${circ * (score / 100)} ${circ}`}
        strokeDashoffset={circ * 0.25} strokeLinecap="round"
        transform="rotate(-90 14 14)" />
      <text x="14" y="18" textAnchor="middle" fontFamily="Plus Jakarta Sans"
        fontSize="7.5" fontWeight="800" fill="var(--navy)">{score}</text>
    </svg>
  );
}

/* ── AI match logic ──────────────────────────────────────────────────────────── */
function getAIRecs(paper) {
  if (!paper) return DOCTORS.filter(d => d.score >= 70).slice(0, 6);
  const pSpec    = (paper.specialty    || '').toLowerCase();
  const pTherapy = (paper.therapy_area || '').toLowerCase();
  let matched = DOCTORS.filter(d => {
    const dSpec  = d.spec.toLowerCase();
    const dIntr  = d.interests.join(' ').toLowerCase();
    return dSpec.includes(pSpec.slice(0, 6)) || pSpec.includes(dSpec.slice(0, 6))
        || dIntr.includes(pTherapy.slice(0, 5)) || dIntr.includes(pSpec.slice(0, 5));
  });
  if (matched.length === 0) matched = DOCTORS.filter(d => d.score >= 70);
  return matched.slice(0, 6);
}

function getMatchReason(doctor, paper) {
  if (!paper) return `High engagement score (${doctor.score})`;
  const pTherapy = (paper.therapy_area || '').toLowerCase();
  const intMatch = doctor.interests.find(i =>
    i.toLowerCase().includes(pTherapy.slice(0, 4)) ||
    pTherapy.includes(i.toLowerCase().slice(0, 4))
  );
  if (intMatch) return `Interest match: ${doctor.interests.slice(0, 2).join(', ')}`;
  return `Specialty match: ${doctor.spec}`;
}

/* ── Doctor card for AI Recommended ─────────────────────────────────────────── */
function RecDocCard({ doctor, selected, paper, onToggle }) {
  return (
    <div
      className={`${styles.recDocCard} ${selected ? styles.recDocCardSel : ''}`}
      onClick={() => onToggle(doctor.id)}
    >
      <div className={styles.recDocAv}>{doctor.init}</div>
      <div className={styles.recDocInfo}>
        <div className={styles.recDocName}>{doctor.name}</div>
        <div className={styles.recDocMeta}>{doctor.spec} · {doctor.city}</div>
        <div className={styles.recDocMatch}>
          <svg width="9" height="9" viewBox="0 0 9 9" fill="none">
            <path d="M4.5.5l.9 2.7H8.5L6.3 4.9l.9 2.7L4.5 6.2 2.3 7.6l.9-2.7L1.5 3.2H4.1L4.5.5z" fill="#7C3AED"/>
          </svg>
          {getMatchReason(doctor, paper)}
        </div>
      </div>
      <div className={styles.recDocRight}>
        <ScoreRing score={doctor.score} />
        <div className={`${styles.recDocCheck} ${selected ? styles.recDocCheckSel : ''}`}>
          {selected && (
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="2,5.5 4,7.5 8,3"/>
            </svg>
          )}
        </div>
      </div>
    </div>
  );
}

/* ── Main component ─────────────────────────────────────────────────────────── */
export default function ShareModal({ paper, onClose, onSent }) {
  const [step,        setStep]       = useState(1);
  const [selIds,      setSelIds]     = useState(new Set());
  const [docSelTab,   setDocSelTab]  = useState('ai');   // 'ai' | 'all'
  const [searchQ,     setSearchQ]    = useState('');
  const [specFilter,  setSpecFilter] = useState('All Specialties');
  const [channel,     setChannel]    = useState('whatsapp');
  const [message,     setMessage]    = useState(
    `Dear Doctor,\n\nHope you're doing well! I came across a recent paper that I thought would be highly relevant to your practice and wanted to share it with you.\n\n"${paper?.title || 'Research Article'}"\n\nWould love your thoughts at your convenience!\n\n— Jijo, Team Life · Mankind Pharma`
  );

  const aiRecs    = useMemo(() => getAIRecs(paper), [paper]);
  const selCount  = selIds.size;

  /* Filtered all-doctors list */
  const allDocs = useMemo(() => {
    return DOCTORS.filter(d => {
      if (searchQ && !d.name.toLowerCase().includes(searchQ.toLowerCase()) &&
          !d.spec.toLowerCase().includes(searchQ.toLowerCase()) &&
          !d.city.toLowerCase().includes(searchQ.toLowerCase())) return false;
      if (specFilter !== 'All Specialties' && d.spec !== specFilter) return false;
      return true;
    });
  }, [searchQ, specFilter]);

  const toggleDoc = (id) => {
    setSelIds(prev => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });
  };

  const toggleAll = (checked) => {
    if (checked) setSelIds(new Set(allDocs.map(d => d.id)));
    else setSelIds(new Set());
  };

  const selectedDoctors = DOCTORS.filter(d => selIds.has(d.id));

  const handleNext = () => {
    if (step === 1 && selCount > 0) setStep(2);
    else if (step === 2) {
      onSent?.(selectedDoctors, channel, message, paper);
      onClose();
    }
  };

  return (
    <div className={styles.overlay} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className={styles.modal}>

        {/* ── Header / Step bar ── */}
        <div className={styles.stepBar}>
          <div className={styles.stepBarLeft}>
            <div className={styles.stepBarIcon}>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="white" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 1L1 7l6 3.5 3 6 6-15.5z"/>
              </svg>
            </div>
            <div>
              <div className={styles.stepBarTitle}>Share Content</div>
              <div className={styles.stepBarSub}>
                {paper ? `${paper.title.slice(0, 55)}…` : 'Select doctors and review message'}
              </div>
            </div>
          </div>
          <div className={styles.stepIndicators}>
            <div className={styles.stepItem}>
              <div className={`${styles.stepNum} ${step === 1 ? styles.stepNumActive : styles.stepNumDone}`}>
                {step > 1 ? '✓' : '1'}
              </div>
              <div className={`${styles.stepLbl} ${step === 1 ? styles.stepLblActive : styles.stepLblDone}`}>Select Doctors</div>
            </div>
            <div className={styles.stepLine} />
            <div className={styles.stepItem}>
              <div className={`${styles.stepNum} ${step === 2 ? styles.stepNumActive : styles.stepNumIdle}`}>2</div>
              <div className={`${styles.stepLbl} ${step === 2 ? styles.stepLblActive : styles.stepLblIdle}`}>Review & Send</div>
            </div>
          </div>
          <button className={styles.closeBtn} onClick={onClose} title="Close">
            <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <line x1="1" y1="1" x2="10" y2="10"/>
              <line x1="10" y1="1" x2="1" y2="10"/>
            </svg>
          </button>
        </div>

        {/* ── Body ── */}
        <div className={styles.body}>

          {/* ══ STEP 1: SELECT DOCTORS ══ */}
          {step === 1 && (
            <div className={styles.step1}>
              {/* Tab switcher */}
              <div className={styles.docSelTabs}>
                <button
                  className={`${styles.dst} ${docSelTab === 'ai' ? styles.dstActive : ''}`}
                  onClick={() => setDocSelTab('ai')}
                >
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M6 .5l1 3H10L7.5 5.3l1 3L6 6.7l-2.5 1.6 1-3L2 3.5h3L6 .5z" fill="#7C3AED" opacity=".9"/>
                  </svg>
                  AI Recommended
                  <span className={styles.dstBadge}>{aiRecs.length}</span>
                </button>
                <button
                  className={`${styles.dst} ${docSelTab === 'all' ? styles.dstActive : ''}`}
                  onClick={() => setDocSelTab('all')}
                >
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
                    <circle cx="5" cy="3.5" r="2"/>
                    <path d="M1.5 11c0-2.5 7-2.5 7 0"/>
                    <line x1="9.5" y1="6" x2="9.5" y2="10"/>
                    <line x1="7.5" y1="8" x2="11.5" y2="8"/>
                  </svg>
                  All Doctors
                </button>
              </div>

              {/* AI Recommended panel */}
              {docSelTab === 'ai' && (
                <div>
                  <div className={styles.aiHint}>
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <path d="M7 1l1.2 3.7H12l-3.1 2.3 1.2 3.7L7 8.2l-3.1 2.3 1.2-3.7L2 4.7h3.8L7 1z" fill="#7C3AED" opacity=".9"/>
                    </svg>
                    Based on <strong>paper specialty</strong> and <strong>doctor interest profiles</strong>, AI recommends these doctors as the best match.
                  </div>
                  <div className={styles.recDocGrid}>
                    {aiRecs.map(doc => (
                      <RecDocCard
                        key={doc.id}
                        doctor={doc}
                        paper={paper}
                        selected={selIds.has(doc.id)}
                        onToggle={toggleDoc}
                      />
                    ))}
                  </div>
                </div>
              )}

              {/* All Doctors panel */}
              {docSelTab === 'all' && (
                <div>
                  <div className={styles.allFilters}>
                    <div className={styles.searchBox}>
                      <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="var(--text4)" strokeWidth="1.6" strokeLinecap="round">
                        <circle cx="5" cy="5" r="4"/>
                        <line x1="8.5" y1="8.5" x2="12" y2="12"/>
                      </svg>
                      <input
                        type="text"
                        placeholder="Search doctors…"
                        value={searchQ}
                        onChange={e => setSearchQ(e.target.value)}
                      />
                    </div>
                    <select
                      className={styles.specSelect}
                      value={specFilter}
                      onChange={e => setSpecFilter(e.target.value)}
                    >
                      {SPECIALTIES.map(s => <option key={s}>{s}</option>)}
                    </select>
                  </div>
                  <div className={styles.allDocsTable}>
                    <table className={styles.miniDt}>
                      <thead>
                        <tr>
                          <th>
                            <input
                              type="checkbox"
                              checked={allDocs.length > 0 && allDocs.every(d => selIds.has(d.id))}
                              onChange={e => toggleAll(e.target.checked)}
                            />
                          </th>
                          <th>Doctor</th>
                          <th>Specialty</th>
                          <th>City</th>
                          <th>Eng. Score</th>
                          <th>Last Engaged</th>
                        </tr>
                      </thead>
                      <tbody>
                        {allDocs.map(doc => (
                          <tr
                            key={doc.id}
                            className={selIds.has(doc.id) ? styles.rowSelected : ''}
                            onClick={() => toggleDoc(doc.id)}
                            style={{ cursor: 'pointer' }}
                          >
                            <td onClick={e => e.stopPropagation()}>
                              <input
                                type="checkbox"
                                checked={selIds.has(doc.id)}
                                onChange={() => toggleDoc(doc.id)}
                              />
                            </td>
                            <td>
                              <div className={styles.docCell}>
                                <div className={styles.docCellAv}>{doc.init}</div>
                                <span className={styles.docCellName}>{doc.name}</span>
                              </div>
                            </td>
                            <td><span className={styles.specBadge}>{doc.spec}</span></td>
                            <td className={styles.cityCell}>{doc.city}</td>
                            <td>
                              <span style={{ fontFamily: "'Plus Jakarta Sans', sans-serif", fontSize: 12, fontWeight: 700, color: scoreColor(doc.score) }}>
                                {doc.score}
                              </span>
                            </td>
                            <td className={styles.lastCell}>{doc.last}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ══ STEP 2: REVIEW & SEND ══ */}
          {step === 2 && (
            <div className={styles.step2}>

              {/* Recipients */}
              <div className={styles.s2Label}>Sending To</div>
              <div className={styles.recipPills}>
                {selectedDoctors.map(doc => (
                  <div key={doc.id} className={styles.recipPill}>
                    <div className={styles.recipPillAv}>{doc.init}</div>
                    <span className={styles.recipPillName}>{doc.name}</span>
                    <button
                      className={styles.recipPillRemove}
                      onClick={() => toggleDoc(doc.id)}
                      title="Remove"
                    >×</button>
                  </div>
                ))}
              </div>

              {/* Channel */}
              <div className={styles.s2Label}>Channel</div>
              <div className={styles.channelBtns}>
                {CHANNELS.map(ch => (
                  <button
                    key={ch.id}
                    className={`${styles.channelBtn} ${channel === ch.id ? styles.channelBtnActive : ''}`}
                    onClick={() => setChannel(ch.id)}
                  >
                    <span className={styles.channelIcon}>{ch.icon}</span>
                    <span className={styles.channelLbl}>{ch.label}</span>
                  </button>
                ))}
              </div>

              {/* Message preview */}
              <div className={styles.s2LabelRow}>
                <div className={styles.s2Label}>Message Preview</div>
                <span className={styles.aiDraftBadge}>AI Drafted</span>
              </div>
              <div className={styles.waPreview}>
                <div className={styles.waBubble}>{message.replace(/\n/g, '\n')}</div>
              </div>

              {/* Edit textarea */}
              <div className={styles.s2Label}>Edit Message</div>
              <textarea
                className={styles.msgTextarea}
                value={message}
                onChange={e => setMessage(e.target.value)}
                rows={6}
              />
              <div className={styles.msgHint}>
                Each message will be personalised with the doctor's first name automatically.
              </div>

            </div>
          )}
        </div>

        {/* ── Footer ── */}
        <div className={styles.footer}>
          <div className={styles.footerLeft}>
            {step === 2 && (
              <button className={styles.backBtn} onClick={() => setStep(1)}>← Back</button>
            )}
            {step === 1 && selCount > 0 && (
              <div className={styles.selSummary}>
                {selCount} doctor{selCount !== 1 ? 's' : ''} selected
              </div>
            )}
          </div>
          <div className={styles.footerRight}>
            <button className={styles.cancelBtn} onClick={onClose}>Cancel</button>
            <button
              className={`${styles.nextBtn} ${step === 2 ? styles.nextBtnSend : ''}`}
              onClick={handleNext}
              disabled={step === 1 && selCount === 0}
            >
              {step === 1 ? (
                <>Select Doctors →</>
              ) : (
                <>
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M11.5 1L1 5l4 2 2 4 4.5-10z"/>
                  </svg>
                  Send to {selCount} Doctor{selCount !== 1 ? 's' : ''}
                </>
              )}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
