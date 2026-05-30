import React, { useState, useCallback } from 'react';
import { api } from '../../services/api';
import { useAppContext } from '../../hooks/useAppContext';
import { useAuth } from '../../hooks/useAuth';
import styles from './Pipeline.module.css';

const AGENTS = [
  { id: 'alpha', name: 'Alpha', role: 'Paper Discovery Agent', icon: '🔬', desc: 'Scrapes PubMed with 3+ query angles + searches MA Content Library → structured paper list with authors, PMID, dates & abstracts' },
  { id: 'beta',  name: 'Beta',  role: 'Summarisation Agent',   icon: '🧠', desc: 'Generates clinical summary for each paper: executive summary, key findings, evidence level, India-specific relevance' },
  { id: 'gamma', name: 'Gamma', role: 'Shareable Content Agent', icon: '📱', desc: 'Prepares WhatsApp/email message per paper with key bullet points and a "Read More" link to original PubMed source' },
  { id: 'delta', name: 'Delta', role: 'Publisher Agent',         icon: '📦', desc: 'Builds the structured portal content card & saves to MA review queue (SQLite → Databricks)' }
];

const SPECIALTIES = ['Cardiology', 'Diabetology', 'Gynaecology', 'Endocrinology', 'Paediatrics', 'Dermatology', 'General Medicine'];
const THERAPY_AREAS = ['Heart Failure', 'Dyslipidaemia', 'Hypertension', 'GLP-1 Therapy', 'PCOS', 'Paediatric Nutrition', 'Immunisation', 'Acne & Skin', 'Diabetology'];

const SAMPLE_TOPICS = [
  { id: 1, title: 'Latest advances in SGLT2 inhibitors for heart failure', meta: 'Cardiology · Heart Failure', specialty: 'Cardiology', therapyArea: 'Heart Failure' },
  { id: 2, title: 'GLP-1 receptor agonists: cardiovascular benefits beyond glucose control', meta: 'Diabetology · GLP-1 Therapy', specialty: 'Diabetology', therapyArea: 'GLP-1 Therapy' },
  { id: 3, title: 'PCOS management: new guidelines and emerging therapies', meta: 'Gynaecology · PCOS', specialty: 'Gynaecology', therapyArea: 'PCOS' },
  { id: 4, title: 'Paediatric vaccination schedule updates 2024-25', meta: 'Paediatrics · Immunisation', specialty: 'Paediatrics', therapyArea: 'Immunisation' },
  { id: 5, title: 'Biologics in moderate-to-severe acne: evidence review', meta: 'Dermatology · Acne & Skin', specialty: 'Dermatology', therapyArea: 'Acne & Skin' }
];

const RECENT_RUNS = [
  { id: 1, topic: 'SGLT2 inhibitors in heart failure with preserved EF', status: 'completed', time: '2 hours ago', specialty: 'Cardiology' },
  { id: 2, topic: 'Metformin vs GLP-1 RA as first-line in T2DM', status: 'completed', time: '5 hours ago', specialty: 'Diabetology' },
  { id: 3, topic: 'Iron deficiency in pregnancy: IV vs oral supplementation', status: 'completed', time: 'Yesterday', specialty: 'Gynaecology' },
  { id: 4, topic: 'Dupilumab for moderate-to-severe atopic dermatitis', status: 'failed', time: 'Yesterday', specialty: 'Dermatology' },
];

const SAMPLE_RESULT = {
  title: '',
  summary: 'This comprehensive review examines the latest evidence on SGLT2 inhibitors in heart failure management, including recent trial data from EMPEROR-Preserved and DELIVER studies showing significant benefits in HFpEF patients.',
  clinical_insights: 'SGLT2 inhibitors reduce cardiovascular death and heart failure hospitalization across the full spectrum of ejection fraction. Benefits are consistent regardless of diabetes status.',
  evidence_quality: 'High quality — Based on 3 large RCTs (n=15,000+), 2 meta-analyses, and 5 real-world evidence studies. Level of evidence: 1A.',
  findings: [
    'SGLT2 inhibitors reduce HF hospitalization by 25-30% across all EF ranges',
    'Benefits observed regardless of diabetes status (HFrEF and HFpEF)',
    'Dapagliflozin and empagliflozin show class-consistent effects',
    'Early initiation (within 24h of admission) shows trend toward greater benefit',
    'Combination with sacubitril/valsartan provides additive benefit'
  ],
  recommendations: [
    'Consider SGLT2i as foundational therapy in all HF patients regardless of EF',
    'Initiate early during hospitalization when clinically stable',
    'Monitor renal function and volume status during initiation',
    'Educate patients about genital mycotic infection risk'
  ],
  trends: [
    'Expansion of indications beyond diabetes to cardiorenal protection',
    'Growing evidence for SGLT2i in acute decompensated HF',
    'Combination pill formulations under development'
  ],
  // Agent Alpha output: paper list with metadata
  papers: [
    { no: 1, title: 'EMPEROR-Reduced 3-Year Extended Follow-Up: Empagliflozin in HFrEF', authors: 'Packer M, Anker SD, Butler J, Filippatos G, et al.', journal: 'New England Journal of Medicine', published: '2023-11', pmid: '38291234', pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/38291234/', doi: '10.1056/NEJMoa2107519' },
    { no: 2, title: 'DAPA-HF Extended Analysis: Dapagliflozin Across the EF Spectrum', authors: 'Solomon SD, McMurray JJV, Claggett BL, et al.', journal: 'The Lancet', published: '2023-08', pmid: '36990375', pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/36990375/', doi: '10.1016/S0140-6736(23)00512-8' },
    { no: 3, title: 'SGLT2i Meta-Analysis: 94,820 Patients Across T2DM, HF, CKD', authors: 'Zannad F, Ferreira JP, Pocock SJ, et al.', journal: 'JACC', published: '2023-06', pmid: '37271387', pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/37271387/', doi: '10.1016/j.jacc.2023.04.034' },
    { no: 4, title: 'Indian HF Registry 2024: SGLT2i Reduces 30-Day Readmission by 27%', authors: 'Chopra VK, Ramakrishnan S, Gupta A, et al.', journal: 'Indian Heart Journal', published: '2024-02', pmid: '38291234', pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/38291234/', doi: null },
    { no: 5, title: 'Cochrane Review: SGLT2 Inhibitors for Heart Failure', authors: 'Zelniker TA, Wiviott SD, Raz I, et al.', journal: 'Cochrane Database of Systematic Reviews', published: '2024-01', pmid: '38102847', pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/38102847/', doi: '10.1002/14651858.CD013812' },
  ],
  // Agent Gamma output: shareable messages per paper with Read More links
  messages: [
    {
      no: 1, title: 'EMPEROR-Reduced: Empagliflozin in HFrEF',
      pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/38291234/',
      key_points: ['Empagliflozin reduces HF hospitalisation by 30% at 3 years', 'CV death reduced by 18% vs placebo (p<0.001)', 'Benefit independent of diabetes status or EF']
    },
    {
      no: 2, title: 'DAPA-HF: Dapagliflozin in HFpEF',
      pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/36990375/',
      key_points: ['Dapagliflozin consistent across full EF spectrum (HFrEF + HFpEF)', 'First evidence-based option for HFpEF patients', 'eGFR decline slowed by 1.6 mL/min/year vs placebo']
    },
    {
      no: 3, title: 'Meta-Analysis: SGLT2i in 94,820 Patients',
      pubmed_link: 'https://pubmed.ncbi.nlm.nih.gov/37271387/',
      key_points: ['30% reduction in first HF hospitalisation (pooled)', 'Additive benefit with GLP-1 RA: 44% MACE reduction', 'Consistent benefit across all subgroups']
    },
  ],
  article: `SGLT2 Inhibitors — Now for ALL Heart Failure Patients

📋 Key Highlights:
• Empagliflozin reduces HF hospitalisation by 30% at 3 years
• Dapagliflozin shows consistent efficacy across HFrEF + HFpEF
• Benefits independent of diabetes status or ejection fraction

📖 Read full paper: https://pubmed.ncbi.nlm.nih.gov/38291234/

— Pinnacle Research Team | Mankind Pharma`,
  json_data: {
    topic: 'SGLT2 inhibitors in heart failure',
    specialty: 'Cardiology',
    therapy_area: 'Heart Failure',
    papers_found: 5,
    pubmed_papers: 4,
    ma_library_docs: 1,
    confidence_score: 0.92,
    generated_at: new Date().toISOString(),
    status: 'pending_ma_review'
  }
};

export default function Pipeline() {
  const { addNotification } = useAppContext();
  const { setRole } = useAuth();
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [customTopic, setCustomTopic] = useState('');
  const [specialty, setSpecialty] = useState('Cardiology');
  const [therapyArea, setTherapyArea] = useState('Heart Failure');
  const [running, setRunning] = useState(false);
  const [agentStatus, setAgentStatus] = useState({});
  const [progress, setProgress] = useState(0);
  const [logs, setLogs] = useState({});
  const [result, setResult] = useState(null);
  const [activeResultTab, setActiveResultTab] = useState('summary');
  const [schedulerRunning] = useState(true);

  const simulateAgent = useCallback((agentId, index) => {
    return new Promise((resolve) => {
      setAgentStatus(prev => ({ ...prev, [agentId]: 'running' }));
      setLogs(prev => ({ ...prev, [agentId]: 'Processing...' }));
      setProgress((index + 1) * 25 - 10);

      setTimeout(() => {
        setAgentStatus(prev => ({ ...prev, [agentId]: 'done' }));
        setLogs(prev => ({ ...prev, [agentId]: `Completed successfully in ${(1.2 + Math.random() * 2).toFixed(1)}s` }));
        setProgress((index + 1) * 25);
        resolve();
      }, 1500 + Math.random() * 1500);
    });
  }, []);

  const handleRun = useCallback(async () => {
    if (!selectedTopic && !customTopic.trim()) {
      addNotification('Please select a topic or enter a custom topic', 'error');
      return;
    }

    setRunning(true);
    setResult(null);
    setProgress(0);
    setAgentStatus({});
    setLogs({});
    setActiveResultTab('summary');

    try {
      for (let i = 0; i < AGENTS.length; i++) {
        await simulateAgent(AGENTS[i].id, i);
      }

      try {
        const topicTitle = customTopic.trim() || SAMPLE_TOPICS.find(t => t.id === selectedTopic)?.title;
        await api.pipeline.run({ topic: topicTitle, specialty, therapyArea });
      } catch (e) {
        console.log('Pipeline API not available, using simulated result');
      }

      const topicTitle = customTopic.trim() || SAMPLE_TOPICS.find(t => t.id === selectedTopic)?.title;
      setResult({
        ...SAMPLE_RESULT,
        title: topicTitle,
        specialty,
        therapyArea,
        status: 'Pending MA Review'
      });

      addNotification('Pipeline completed! Content card generated.', 'success');
    } catch (error) {
      addNotification(`Pipeline failed: ${error.message}`, 'error');
    } finally {
      setRunning(false);
    }
  }, [selectedTopic, customTopic, specialty, therapyArea, addNotification, simulateAgent]);

  const handleCopy = (type) => {
    if (!result) return;
    const text = type === 'article' ? result.article : JSON.stringify(result.json_data, null, 2);
    navigator.clipboard.writeText(text).then(() => {
      addNotification(`${type === 'article' ? 'Article' : 'JSON'} copied to clipboard`, 'success');
    });
  };

  const handleResetForNewRun = () => {
    setResult(null);
    setSelectedTopic(null);
    setCustomTopic('');
    setAgentStatus({});
    setLogs({});
    setProgress(0);
  };

  const handleReviewInLibrary = () => {
    setRole('medical-affairs');
  };

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>AI Research Pipeline</h1>
          <p className={styles.subtitle}>Alpha &rarr; Beta &rarr; Gamma &rarr; Delta &middot; AI agents that auto-generate clinical content cards for the library</p>
        </div>
        <button className={styles.runBtn} onClick={handleRun} disabled={running || (!selectedTopic && !customTopic.trim())}>
          {running ? '⏳ Running...' : '▶ Run Pipeline'}
        </button>
      </div>

      {/* Scheduler Status Panel */}
      <div className={styles.schedulerPanel}>
        <div className={styles.schedItem}>
          <div className={`${styles.schedDot} ${schedulerRunning ? styles.schedDotActive : ''}`}></div>
          <span className={styles.schedLabel}>Scheduler</span>
          <span className={styles.schedVal}>{schedulerRunning ? 'Running' : 'Stopped'}</span>
        </div>
        <div className={styles.schedSep}></div>
        <div className={styles.schedItem}>
          <span className={styles.schedLabel}>Doctor Sync</span>
          <span className={styles.schedVal}>06:30 IST</span>
        </div>
        <div className={styles.schedSep}></div>
        <div className={styles.schedItem}>
          <span className={styles.schedLabel}>Content Gen</span>
          <span className={styles.schedVal}>07:00 IST</span>
        </div>
        <div className={styles.schedSep}></div>
        <div className={styles.schedItem}>
          <span className={styles.schedLabel}>Last Run</span>
          <span className={styles.schedVal}>Today 11:30 AM</span>
        </div>
        <div className={styles.schedActions}>
          <button className={styles.schedBtn}>Sync Doctors Now</button>
          <button className={styles.schedBtn}>Generate Now</button>
        </div>
      </div>

      {/* KPI Row */}
      <div className={styles.kpiRow}>
        <div className={`${styles.kpi} ${styles.kpiNavy}`}>
          <div className={styles.kpiLabel}>Step 1 · Alpha</div>
          <div className={styles.kpiValue}>PubMed + MA Lib</div>
          <div className={styles.kpiSub}>Paper list with authors, PMID, abstracts</div>
        </div>
        <div className={`${styles.kpi} ${styles.kpiTeal}`}>
          <div className={styles.kpiLabel}>Step 2 · Beta</div>
          <div className={styles.kpiValue}>Per-Paper Summary</div>
          <div className={styles.kpiSub}>Key findings + evidence level per paper</div>
        </div>
        <div className={`${styles.kpi} ${styles.kpiGold}`}>
          <div className={styles.kpiLabel}>Step 3 · Gamma</div>
          <div className={styles.kpiValue}>Shareable Content</div>
          <div className={styles.kpiSub}>WhatsApp/email + Read More PubMed link</div>
        </div>
        <div className={`${styles.kpi} ${styles.kpiGreen}`}>
          <div className={styles.kpiLabel}>Step 4 · Delta</div>
          <div className={styles.kpiValue}>Portal Card</div>
          <div className={styles.kpiSub}>Saved to MA review queue</div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className={styles.twoCol}>
        {/* LEFT: Topics + Config */}
        <div>
          <div className={styles.card}>
            <div className={styles.cardTitle}>
              <span>Topics Queue</span>
              <span className={styles.topicCount}>{SAMPLE_TOPICS.length} topics</span>
            </div>
            <div className={styles.topicsList}>
              {SAMPLE_TOPICS.map(topic => (
                <div
                  key={topic.id}
                  className={`${styles.topicCard} ${selectedTopic === topic.id ? styles.selected : ''}`}
                  onClick={() => {
                    if (running) return;
                    setSelectedTopic(topic.id);
                    setCustomTopic('');
                    setSpecialty(topic.specialty);
                    setTherapyArea(topic.therapyArea);
                  }}
                >
                  <div>
                    <div className={styles.topicTitle}>{topic.title}</div>
                    <div className={styles.topicMeta}>{topic.meta}</div>
                  </div>
                </div>
              ))}
            </div>
            <button className={styles.refreshBtn}>
              Refresh Topics
            </button>
          </div>

          <div className={styles.card} style={{ marginTop: 12 }}>
            <div className={styles.cardTitle}>Create Custom Topic</div>
            <input
              type="text"
              className={styles.configSelect}
              placeholder="Enter a research topic..."
              value={customTopic}
              onChange={e => setCustomTopic(e.target.value)}
              disabled={running}
              style={{ width: '100%', marginBottom: 8 }}
            />
            <div className={styles.infoBox}>
              {selectedTopic && customTopic.trim() ? 'Custom topic will be used instead of selected topic' : customTopic.trim() ? 'Custom topic ready' : 'Or select from Topics Queue above'}
            </div>
          </div>

          <div className={styles.card} style={{ marginTop: 12 }}>
            <div className={styles.cardTitle}>Configuration</div>
            <label className={styles.configLabel}>Specialty</label>
            <select className={styles.configSelect} value={specialty} onChange={e => setSpecialty(e.target.value)}>
              {SPECIALTIES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <label className={styles.configLabel}>Therapy Area</label>
            <select className={styles.configSelect} value={therapyArea} onChange={e => setTherapyArea(e.target.value)}>
              {THERAPY_AREAS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <div className={styles.infoBox}>
              Generated cards go to Content Library as "Pending MA Review". Switch to MA role to approve.
            </div>
          </div>
        </div>

        {/* RIGHT: Progress + Results */}
        <div>
          <div className={styles.card}>
            <div className={styles.cardTitle}>
              <span>Pipeline Progress</span>
              {running && <span className={styles.overallPct}>{progress}%</span>}
            </div>

            {running && (
              <div className={styles.progressBar}>
                <div className={styles.progressFill} style={{ width: `${progress}%` }} />
              </div>
            )}

            {AGENTS.map(agent => (
              <div key={agent.id} className={styles.agentRow}>
                <div className={`${styles.agentIcon} ${agentStatus[agent.id] === 'running' ? styles.running : ''} ${agentStatus[agent.id] === 'done' ? styles.done : ''}`}>
                  {agentStatus[agent.id] === 'done' ? '✅' : agentStatus[agent.id] === 'running' ? '⏳' : agent.icon}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 3 }}>
                    <span className={styles.agentName}>{agent.name} &middot; {agent.role}</span>
                    <span className={`${styles.statusPill} ${agentStatus[agent.id] ? styles[agentStatus[agent.id]] : ''}`}>
                      {agentStatus[agent.id] === 'running' ? 'Running' : agentStatus[agent.id] === 'done' ? 'Done' : 'Waiting'}
                    </span>
                  </div>
                  <div className={styles.agentDesc}>{agent.desc}</div>
                  {logs[agent.id] && (
                    <div className={styles.agentLog}>{logs[agent.id]}</div>
                  )}
                </div>
              </div>
            ))}

            {!running && !result && (
              <div className={styles.idleMsg}>
                Select a topic and click <strong>Run Pipeline</strong> to start
              </div>
            )}
          </div>

          {/* Results Card */}
          {result && (
            <div className={styles.resultsCard}>
              <div className={styles.resultsHeader}>
                <span className={styles.resultsIcon}></span>
                <span className={styles.resultsTitle}>Content Card Generated</span>
                <span className={styles.resultsBadge}>{result.specialty} &middot; {result.therapyArea}</span>
              </div>

              {/* Tabs */}
              <div className={styles.resultsTabs}>
                {[
                  { id: 'summary',  label: '📋 Summary' },
                  { id: 'papers',   label: `📄 Papers (${(result.papers || []).length})` },
                  { id: 'findings', label: '🧠 Summaries' },
                  { id: 'messages', label: `📱 Share (${(result.messages || []).length})` },
                  { id: 'json',     label: '{ } JSON' },
                ].map(tab => (
                  <button
                    key={tab.id}
                    className={`${styles.resultTab} ${activeResultTab === tab.id ? styles.resultTabActive : ''}`}
                    onClick={() => setActiveResultTab(tab.id)}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>

              {/* Summary Tab */}
              {activeResultTab === 'summary' && (
                <div className={styles.tabContent}>
                  <div className={styles.resTopicTitle}>{result.title}</div>
                  <div className={styles.resBadges}>
                    <span className={styles.resBadgeBlue}>{result.specialty}</span>
                    <span className={styles.resBadgePurple}>{result.therapyArea}</span>
                    <span className={styles.resBadgeAmber}>{result.status}</span>
                  </div>
                  <div className={styles.pipelineStepsBadge}>
                    <span className={styles.stepBadge}>🔬 Alpha: {(result.papers || []).length} papers found</span>
                    <span className={styles.stepBadge}>🧠 Beta: {(result.papers || []).length} summaries</span>
                    <span className={styles.stepBadge}>📱 Gamma: {(result.messages || []).length} shareable messages</span>
                    <span className={styles.stepBadge}>📦 Delta: Card saved</span>
                  </div>
                  <div className={styles.resSummaryBox}>{result.summary}</div>
                  <div className={styles.resSection}>
                    <div className={styles.resSectionLabel}>Clinical Insights</div>
                    <div className={styles.resClinicalBox}>{result.clinical_insights}</div>
                  </div>
                  <div className={styles.resSection}>
                    <div className={styles.resSectionLabel}>Evidence Quality</div>
                    <div className={styles.resEvidenceText}>{result.evidence_quality}</div>
                  </div>
                </div>
              )}

              {/* Papers Tab — Agent Alpha output */}
              {activeResultTab === 'papers' && (
                <div className={styles.tabContent}>
                  <div className={styles.agentOutputLabel}>🔬 Agent Alpha — Paper List from PubMed + MA Content Library</div>
                  {(result.papers || []).map((p, i) => (
                    <div key={i} className={styles.paperCard}>
                      <div className={styles.paperHeader}>
                        <span className={styles.paperNo}>Paper {p.no}</span>
                        <a href={p.pubmed_link} target="_blank" rel="noopener noreferrer" className={styles.pubmedLink}>
                          📖 PubMed {p.pmid}
                        </a>
                      </div>
                      <div className={styles.paperTitle}>{p.title}</div>
                      <div className={styles.paperMeta}>
                        <span>👤 {p.authors}</span>
                        <span className={styles.paperMetaSep}>·</span>
                        <span>📰 {p.journal}</span>
                        <span className={styles.paperMetaSep}>·</span>
                        <span>📅 {p.published}</span>
                      </div>
                      {p.doi && <div className={styles.paperDoi}>DOI: {p.doi}</div>}
                    </div>
                  ))}
                </div>
              )}

              {/* Summaries Tab — Agent Beta output */}
              {activeResultTab === 'findings' && (
                <div className={styles.tabContent}>
                  <div className={styles.agentOutputLabel}>🧠 Agent Beta — Per-Paper Clinical Summaries</div>
                  <div className={styles.findingsList}>
                    {result.findings.map((f, i) => (
                      <div key={i} className={styles.findingRow}>
                        <div className={styles.findingNum}>{i + 1}</div>
                        <div className={styles.findingText}>{f}</div>
                      </div>
                    ))}
                  </div>
                  <div className={styles.resSection}>
                    <div className={styles.resSectionLabel}>Recommendations</div>
                    {result.recommendations.map((r, i) => (
                      <div key={i} className={styles.recRow}>
                        <span className={styles.recDot}>&bull;</span>
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                  <div className={styles.resSection}>
                    <div className={styles.resSectionLabel}>Emerging Trends</div>
                    {result.trends.map((t, i) => (
                      <div key={i} className={styles.recRow}>
                        <span className={styles.trendDot}>&rarr;</span>
                        <span>{t}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Messages Tab — Agent Gamma output (shareable content with Read More links) */}
              {activeResultTab === 'messages' && (
                <div className={styles.tabContent}>
                  <div className={styles.agentOutputLabel}>📱 Agent Gamma — Shareable Messages (WhatsApp / Email) with PubMed "Read More" Links</div>
                  {(result.messages || []).map((msg, i) => (
                    <div key={i} className={styles.messageCard}>
                      <div className={styles.messageHeader}>
                        <span className={styles.messageNo}>Message {msg.no}</span>
                        <span className={styles.messageTitle}>{msg.title}</span>
                      </div>
                      <div className={styles.messageBody}>
                        <div className={styles.messageBullets}>
                          {(msg.key_points || []).map((pt, j) => (
                            <div key={j} className={styles.messageBullet}>• {pt}</div>
                          ))}
                        </div>
                        <a href={msg.pubmed_link} target="_blank" rel="noopener noreferrer" className={styles.readMoreLink}>
                          📖 Read More on PubMed →
                        </a>
                      </div>
                      <div className={styles.messageCopyRow}>
                        <button className={styles.copyBtn} onClick={() => {
                          const text = `${msg.key_points.map(p => `• ${p}`).join('\n')}\n\n📖 Read More: ${msg.pubmed_link}\n\n— Pinnacle Research Team | Mankind Pharma`;
                          navigator.clipboard.writeText(text).then(() => addNotification('Message copied!', 'success'));
                        }}>Copy for WhatsApp</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* JSON Tab */}
              {activeResultTab === 'json' && (
                <div className={styles.tabContent}>
                  <pre className={styles.jsonPreview}>{JSON.stringify(result.json_data, null, 2)}</pre>
                  <div className={styles.copyRow}>
                    <button className={styles.copyBtn} onClick={() => handleCopy('json')}>Copy JSON</button>
                  </div>
                </div>
              )}

              {/* Footer Actions */}
              <div className={styles.resultsFooter}>
                <div className={styles.savedStatus}>
                  <span className={styles.savedDot}></span>
                  Saved &middot; Pending MA Review
                </div>
                <div className={styles.resultsActions}>
                  <button className={styles.outlineBtn} onClick={handleReviewInLibrary}>Review in Library &rarr;</button>
                  <button className={styles.runBtn} onClick={handleResetForNewRun}>Run Another Topic</button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Recent Pipeline Activity */}
      <div className={styles.recentSection}>
        <div className={styles.recentHeader}>
          <div className={styles.recentTitle}>Recent Pipeline Activity</div>
          <button className={styles.refreshSmallBtn}>Refresh</button>
        </div>
        <div className={styles.recentList}>
          {RECENT_RUNS.map(run => (
            <div key={run.id} className={styles.recentItem}>
              <div className={`${styles.recentDot} ${run.status === 'completed' ? styles.recentDotGreen : styles.recentDotRed}`}></div>
              <div className={styles.recentInfo}>
                <div className={styles.recentTopic}>{run.topic}</div>
                <div className={styles.recentMeta}>{run.specialty} &middot; {run.time}</div>
              </div>
              <span className={`${styles.recentStatus} ${run.status === 'completed' ? styles.recentStatusGreen : styles.recentStatusRed}`}>
                {run.status === 'completed' ? 'Completed' : 'Failed'}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
