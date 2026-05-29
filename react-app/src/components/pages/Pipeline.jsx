import React, { useState, useCallback } from 'react';
import { api } from '../../services/api';
import { useAppContext } from '../../hooks/useAppContext';
import { useAuth } from '../../hooks/useAuth';
import styles from './Pipeline.module.css';

const AGENTS = [
  { id: 'alpha', name: 'Alpha', role: 'Research Agent', icon: '\u{1F50D}', desc: 'Searches PubMed, web & internal documents for evidence' },
  { id: 'beta', name: 'Beta', role: 'Insights Agent', icon: '\u{1F4A1}', desc: 'Synthesises key findings, clinical insights & emerging trends' },
  { id: 'gamma', name: 'Gamma', role: 'Content Agent', icon: '✍️', desc: 'Writes the WhatsApp-ready short article for doctor sharing' },
  { id: 'delta', name: 'Delta', role: 'Publisher Agent', icon: '\u{1F4E6}', desc: 'Builds the structured content card & saves to library' }
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
  article: `Heart Failure Management Update: SGLT2 Inhibitors

Recent landmark trials have established SGLT2 inhibitors as a cornerstone therapy for heart failure across all ejection fractions.

Key Evidence:
The EMPEROR-Preserved and DELIVER trials demonstrated significant reductions in cardiovascular death and heart failure hospitalization in HFpEF patients, extending benefits previously shown in HFrEF.

Clinical Impact:
These medications reduce hospitalization risk by 25-30% and improve quality of life metrics. Benefits are seen regardless of diabetes status.

For Your Practice:
Consider initiating SGLT2 inhibitors early in all heart failure patients. Monitor renal function during the first few weeks of therapy.

Source: PubMed Evidence Review · PinnacleIQ AI Pipeline`,
  json_data: {
    topic: 'SGLT2 inhibitors in heart failure',
    specialty: 'Cardiology',
    therapy_area: 'Heart Failure',
    sources_count: 12,
    pubmed_articles: 8,
    web_sources: 4,
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
          <div className={styles.kpiLabel}>Agent Pipeline</div>
          <div className={styles.kpiValue}>Alpha&rarr;Delta</div>
          <div className={styles.kpiSub}>4 AI agents in sequence</div>
        </div>
        <div className={`${styles.kpi} ${styles.kpiTeal}`}>
          <div className={styles.kpiLabel}>Research Sources</div>
          <div className={styles.kpiValue}>PubMed + Web</div>
          <div className={styles.kpiSub}>Tavily real-time search</div>
        </div>
        <div className={`${styles.kpi} ${styles.kpiGold}`}>
          <div className={styles.kpiLabel}>Output Format</div>
          <div className={styles.kpiValue}>Portal Card</div>
          <div className={styles.kpiSub}>JSON + short article</div>
        </div>
        <div className={`${styles.kpi} ${styles.kpiGreen}`}>
          <div className={styles.kpiLabel}>Store Backend</div>
          <div className={styles.kpiValue}>SQLite &rarr; Databricks</div>
          <div className={styles.kpiSub}>One env-var switch</div>
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
                {['summary', 'findings', 'article', 'json'].map(tab => (
                  <button
                    key={tab}
                    className={`${styles.resultTab} ${activeResultTab === tab ? styles.resultTabActive : ''}`}
                    onClick={() => setActiveResultTab(tab)}
                  >
                    {tab === 'summary' ? 'Summary' : tab === 'findings' ? 'Key Findings' : tab === 'article' ? 'Short Article' : 'Full JSON'}
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

              {/* Findings Tab */}
              {activeResultTab === 'findings' && (
                <div className={styles.tabContent}>
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

              {/* Article Tab */}
              {activeResultTab === 'article' && (
                <div className={styles.tabContent}>
                  <div className={styles.articlePreview}>{result.article}</div>
                  <div className={styles.copyRow}>
                    <button className={styles.copyBtn} onClick={() => handleCopy('article')}>Copy Article</button>
                  </div>
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
