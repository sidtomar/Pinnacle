/**
 * AddContentWizard — 4-step modal for Medical Affairs to add content
 *
 * Step 1: Choose Source (PubMed Link / Upload PDF / Web Link)
 * Step 2: AI Processing (animated extraction steps)
 * Step 3: Review & Categorise (editable form with AI pre-fill)
 * Step 4: Confirm (success screen)
 */
import React, { useState, useRef } from 'react';
import styles from './AddContentWizard.module.css';

const SPECIALTIES  = ['Cardiology', 'Diabetology', 'Gynaecology', 'Endocrinology', 'Paediatrics', 'Dermatology', 'Oncology', 'General Medicine'];
const THERAPY_AREAS = ['Heart Failure', 'Dyslipidaemia', 'GLP-1 Therapy', 'PCOS', 'Fertility & ART', 'Paediatric Nutrition', 'Immunisation', 'Acne & Skin', 'Hypertension', 'Type 2 Diabetes'];
const SUB_CATEGORIES = ['Meta-Analysis / Systematic Review', 'Clinical Trial / RCT', 'Observational Study', 'Review Article', 'Expert Opinion / Guidelines', 'Case Series'];
const RELEVANCES = ['High', 'Medium', 'Low'];
const REC_FOR = ['All Specialists', 'Cardiologists', 'Diabetologists / Endocrinologists', 'Gynaecologists', 'Paediatricians', 'Dermatologists', 'Oncologists', 'PCOS-focused Gynaecs', 'Internal Medicine'];

// Simulated AI-extracted paper (in production this calls the PubMed API / LLM)
const MOCK_EXTRACTION = {
  title: 'Inositol vs Metformin in PCOS: A Systematic Review and Meta-Analysis',
  journal: 'Fertility & Sterility',
  year: '2025',
  authors: 'Sharma R, Nair P, Venkataraman S, et al.',
  pmid: '39124578',
  summary: 'This meta-analysis of 18 RCTs (n=2,847) demonstrates myo-inositol achieves comparable insulin sensitisation to metformin with significantly fewer GI side effects. Key finding: 78% improvement in menstrual regularity at 6 months vs 64% with metformin (p<0.01). Pregnancy rates significantly higher with inositol in anovulatory PCOS.',
  specialty: 'Gynaecology',
  therapy_area: 'PCOS',
  sub_category: 'Meta-Analysis / Systematic Review',
  relevance: 'High',
  tags: 'PCOS, Inositol, Metformin, RCT, Fertility',
  recommended_for: 'PCOS-focused Gynaecs',
};

const AI_STEPS = [
  'Fetching from source',
  'Extracting metadata & abstract',
  'Generating clinical summary',
  'Suggesting categorisation',
];

// Step indicator in the wizard header
function WizardSteps({ current }) {
  const steps = ['Choose Source', 'AI Processing', 'Review & Categorise', 'Confirm'];
  return (
    <div className={styles.steps}>
      {steps.map((label, i) => {
        const n = i + 1;
        const isDone   = n < current;
        const isActive = n === current;
        return (
          <React.Fragment key={n}>
            <div className={styles.step}>
              <div className={`${styles.stepNum} ${isDone ? styles.stepDone : isActive ? styles.stepActive : styles.stepIdle}`}>
                {isDone ? '✓' : n}
              </div>
              <div className={`${styles.stepLbl} ${n <= current ? styles.stepLblActive : styles.stepLblIdle}`}>
                {label}
              </div>
            </div>
            {i < steps.length - 1 && <div className={styles.stepLine} />}
          </React.Fragment>
        );
      })}
    </div>
  );
}

export default function AddContentWizard({ onClose, onAdded }) {
  const [step,       setStep]      = useState(1);
  const [src,        setSrc]       = useState(null);    // 'pubmed' | 'upload' | 'pdf'
  const [pmInput,    setPmInput]   = useState('');
  const [linkInput,  setLinkInput] = useState('');
  const [fileName,   setFileName]  = useState(null);
  const [aiStepDone, setAiStepDone] = useState(0);     // how many AI steps are done
  const [dragOver,   setDragOver]  = useState(false);

  // Step 3 form state (pre-filled from AI extraction)
  const [form, setForm] = useState({ ...MOCK_EXTRACTION });

  const fileInputRef = useRef(null);

  /* ── helpers ── */
  const updateForm = (key, val) => setForm(prev => ({ ...prev, [key]: val }));

  function handleFileSelect(file) {
    if (!file || file.type !== 'application/pdf') return;
    setFileName(file.name);
  }

  function startProcessing() {
    setStep(2);
    setAiStepDone(0);
    // Simulate AI extraction steps
    [1000, 2100, 3200, 4000].forEach((ms, i) => {
      setTimeout(() => setAiStepDone(i + 1), ms);
    });
    setTimeout(() => setStep(3), 4400);
  }

  function handleNext() {
    if (step === 1) {
      if (!src) return;
      startProcessing();
    } else if (step === 3) {
      // Add to library
      const newCard = {
        id: Date.now(),
        status: 'approved',          // MA uploads are auto-approved
        source: src,
        title: form.title,
        journal: form.journal + ', ' + form.year,
        authors: form.authors,
        pmid: form.pmid,
        summary: form.summary,
        specialty: form.specialty,
        therapy_area: form.therapy_area,
        sub_category: form.sub_category,
        relevance: form.relevance,
        tags: form.tags.split(',').map(t => t.trim()).filter(Boolean),
        recommended_for: form.recommended_for,
        date: new Date().toISOString().slice(0, 10),
        reviewer: 'Dr. Prashant Agarwal',
      };
      onAdded?.(newCard);
      setStep(4);
    } else if (step === 4) {
      onClose();
    }
  }

  function handleBack() {
    if (step === 3) setStep(1);
  }

  const canNext = step === 1 ? !!src : step === 3 ? form.title.trim().length > 0 : true;

  /* ── render ── */
  return (
    <div className={styles.overlay} onClick={e => { if (e.target === e.currentTarget) onClose(); }}>
      <div className={styles.modal}>

        {/* Header */}
        <div className={styles.header}>
          <WizardSteps current={step} />
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        {/* Body */}
        <div className={styles.body}>

          {/* ── Step 1: Choose Source ── */}
          {step === 1 && (
            <div>
              <div className={styles.stepTitle}>Add New Content</div>
              <div className={styles.stepDesc}>How would you like to add this content?</div>

              <div className={styles.srcCards}>
                {[
                  { id: 'pubmed', icon: '🔬', color: 'var(--blue-bg)', stroke: 'var(--blue)', name: 'PubMed Link', desc: 'Paste a PubMed URL or PMID' },
                  { id: 'upload', icon: '⬆️', color: 'var(--purple-bg)', stroke: 'var(--purple)', name: 'Upload PDF', desc: 'Research paper, guideline or newsletter' },
                  { id: 'link',   icon: '🔗', color: 'var(--amber-bg)',  stroke: 'var(--amber)',  name: 'Web Link', desc: 'Article or online resource URL' },
                ].map(s => (
                  <div
                    key={s.id}
                    className={`${styles.srcCard} ${src === s.id ? styles.srcCardSel : ''}`}
                    onClick={() => setSrc(s.id)}
                  >
                    <div className={styles.srcIcon} style={{ background: s.color, fontSize: 22 }}>{s.icon}</div>
                    <div className={styles.srcName}>{s.name}</div>
                    <div className={styles.srcDesc}>{s.desc}</div>
                  </div>
                ))}
              </div>

              {/* PubMed input */}
              {src === 'pubmed' && (
                <div className={styles.srcInputArea}>
                  <label className={styles.fieldLabel}>PubMed URL or PMID</label>
                  <div style={{ display: 'flex', gap: 10 }}>
                    <input
                      className={styles.textInput}
                      style={{ flex: 1 }}
                      type="text"
                      placeholder="https://pubmed.ncbi.nlm.nih.gov/… or PMID number"
                      value={pmInput}
                      onChange={e => setPmInput(e.target.value)}
                    />
                    <button className={styles.fetchBtn} onClick={startProcessing} disabled={!pmInput.trim()}>
                      Fetch →
                    </button>
                  </div>
                  <div className={styles.inputHint}>AI will extract title, abstract, authors, journal and generate a clinical summary.</div>
                </div>
              )}

              {/* Upload PDF input */}
              {src === 'upload' && (
                <div className={styles.srcInputArea}>
                  {!fileName ? (
                    <div
                      className={`${styles.uploadZone} ${dragOver ? styles.uploadDrag : ''}`}
                      onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                      onDragLeave={() => setDragOver(false)}
                      onDrop={e => {
                        e.preventDefault();
                        setDragOver(false);
                        const f = e.dataTransfer.files[0];
                        if (f?.type === 'application/pdf') handleFileSelect(f);
                      }}
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <div className={styles.uploadIcon}>📄</div>
                      <div className={styles.uploadText}>
                        <strong>Drag & drop PDF here</strong> or <span className={styles.browseLink}>Browse</span>
                      </div>
                      <div className={styles.uploadHint}>PDF only · Max 25 MB</div>
                      <input
                        ref={fileInputRef}
                        type="file"
                        accept=".pdf"
                        style={{ display: 'none' }}
                        onChange={e => handleFileSelect(e.target.files[0])}
                      />
                    </div>
                  ) : (
                    <div className={styles.fileSelected}>
                      <div className={styles.fileIcon}>📄</div>
                      <div>
                        <div className={styles.fileName}>{fileName}</div>
                        <div className={styles.fileHint}>Ready to process</div>
                      </div>
                      <button className={styles.processBtn} onClick={startProcessing}>
                        Process with AI →
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Web Link input */}
              {src === 'link' && (
                <div className={styles.srcInputArea}>
                  <label className={styles.fieldLabel}>Web Article URL</label>
                  <div style={{ display: 'flex', gap: 10 }}>
                    <input
                      className={styles.textInput}
                      style={{ flex: 1 }}
                      type="url"
                      placeholder="https://…"
                      value={linkInput}
                      onChange={e => setLinkInput(e.target.value)}
                    />
                    <button className={styles.fetchBtn} onClick={startProcessing} disabled={!linkInput.trim()}>
                      Extract →
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ── Step 2: AI Processing ── */}
          {step === 2 && (
            <div className={styles.aiProc}>
              <div className={`${styles.aiSpinner} ${aiStepDone >= AI_STEPS.length ? styles.aiDone : ''}`}>
                {aiStepDone >= AI_STEPS.length ? '✅' : ''}
              </div>
              <div className={styles.aiTitle}>
                {aiStepDone >= AI_STEPS.length ? 'Extraction complete!' : 'AI extracting paper details…'}
              </div>
              <div className={styles.aiStepList}>
                {AI_STEPS.map((label, i) => {
                  const done    = i < aiStepDone;
                  const current = i === aiStepDone;
                  return (
                    <div key={i} className={`${styles.aiStep} ${done ? styles.aiStepDone : current ? styles.aiStepCurr : ''}`}>
                      {done ? (
                        <span className={styles.aiStepIcon}>✅</span>
                      ) : current ? (
                        <span className={styles.aiStepIcon}>🔄</span>
                      ) : (
                        <span className={styles.aiStepIcon}>⏳</span>
                      )}
                      {done ? label.replace('…', '') : label}{current ? '…' : ''}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Step 3: Review & Categorise ── */}
          {step === 3 && (
            <div>
              {/* Success notice */}
              <div className={styles.successNotice}>
                <span>✅</span>
                <span><strong>AI extracted paper details.</strong> Review and edit before saving.</span>
              </div>

              {/* Extracted paper header */}
              <div className={styles.extractedPaper}>
                <div className={styles.extTitle}>{form.title}</div>
                <div className={styles.extMeta}>
                  <span>📰 {form.journal}{form.year ? `, ${form.year}` : ''}</span>
                  <span>👤 {form.authors}</span>
                  {form.pmid && <span>🔬 PMID: {form.pmid}</span>}
                </div>
              </div>

              {/* Editable summary */}
              <label className={styles.fieldLabel}>
                AI Clinical Summary
                <span className={styles.editableBadge}>Editable</span>
              </label>
              <textarea
                className={styles.summaryTextarea}
                value={form.summary}
                onChange={e => updateForm('summary', e.target.value)}
                rows={4}
              />

              {/* 2-col fields */}
              <div className={styles.fieldGrid}>
                <div>
                  <label className={styles.fieldLabel}>Specialty</label>
                  <select className={styles.fieldSelect} value={form.specialty} onChange={e => updateForm('specialty', e.target.value)}>
                    {SPECIALTIES.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className={styles.fieldLabel}>Therapy Area</label>
                  <select className={styles.fieldSelect} value={form.therapy_area} onChange={e => updateForm('therapy_area', e.target.value)}>
                    {THERAPY_AREAS.map(t => <option key={t}>{t}</option>)}
                  </select>
                </div>
                <div>
                  <label className={styles.fieldLabel}>Sub-category</label>
                  <select className={styles.fieldSelect} value={form.sub_category} onChange={e => updateForm('sub_category', e.target.value)}>
                    {SUB_CATEGORIES.map(s => <option key={s}>{s}</option>)}
                  </select>
                </div>
                <div>
                  <label className={styles.fieldLabel}>Relevance</label>
                  <select className={styles.fieldSelect} value={form.relevance} onChange={e => updateForm('relevance', e.target.value)}>
                    {RELEVANCES.map(r => <option key={r}>{r}</option>)}
                  </select>
                </div>
              </div>

              <label className={styles.fieldLabel}>Tags <span className={styles.fieldHint}>(comma-separated)</span></label>
              <input
                className={styles.textInput}
                value={form.tags}
                onChange={e => updateForm('tags', e.target.value)}
                placeholder="PCOS, Inositol, RCT"
                style={{ marginBottom: 12 }}
              />

              <label className={styles.fieldLabel}>Recommended For</label>
              <select className={styles.fieldSelect} style={{ marginBottom: 14 }} value={form.recommended_for} onChange={e => updateForm('recommended_for', e.target.value)}>
                {REC_FOR.map(r => <option key={r}>{r}</option>)}
              </select>

              {/* Auto-approve note */}
              <div className={styles.autoApproveNote}>
                ⚠️ MA-uploaded content is <strong> auto-approved</strong> and immediately available to PMT.
              </div>
            </div>
          )}

          {/* ── Step 4: Success ── */}
          {step === 4 && (
            <div className={styles.successScreen}>
              <div className={styles.successCircle}>✓</div>
              <div className={styles.successTitle}>Content Added Successfully</div>
              <div className={styles.successSub}>
                Now live in the library and available for PMT to share with doctors.
              </div>
            </div>
          )}

        </div>

        {/* Footer */}
        <div className={styles.footer}>
          {step > 1 && step < 4 && step !== 2 && (
            <button className={styles.backBtn} onClick={handleBack}>← Back</button>
          )}
          <div style={{ flex: 1 }} />
          {step !== 2 && (
            <button
              className={`${styles.nextBtn} ${step === 4 ? styles.nextBtnGreen : ''}`}
              onClick={handleNext}
              disabled={!canNext}
            >
              {step === 1 && 'Next →'}
              {step === 3 && 'Add to Library →'}
              {step === 4 && 'Done ✓'}
            </button>
          )}
        </div>

      </div>
    </div>
  );
}
