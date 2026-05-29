import React, { useState, useMemo } from 'react';
import { useAppContext } from '../../hooks/useAppContext';
import styles from './TodaysTasks.module.css';

const TASKS = [
  { id: 't1', priority: 'urgent', type: 'birthday', icon: '🎂', title: 'Birthday tomorrow',
    doctor: 'Dr. Priya Nair', spec: 'Gynaecologist', city: 'Bangalore', cat: 'A+', score: 81, initials: 'PN',
    action: 'Send Birthday Wish', hint: '2 May 2026 · Consider sending a bouquet via Ferns N Petals' },
  { id: 't2', priority: 'urgent', type: 'overdue', icon: '🚨', title: 'Never received content',
    doctor: 'Dr. S.K. Singh', spec: 'Endocrinologist', city: 'Varanasi', cat: 'A+', score: 18, initials: 'SS',
    action: 'Send First Paper', hint: 'Engagement score critically low — first send overdue since onboarding' },
  { id: 't3', priority: 'urgent', type: 'overdue', icon: '⚠️', title: '31 days without engagement',
    doctor: 'Dr. Giridhari Jena', spec: 'Cardiologist', city: 'Bhubaneswar', cat: 'A', score: 44, initials: 'GJ',
    action: 'Re-engage Now', hint: 'Last sent: Telmisartan Trial · 22 Mar 2026 — now 31 days overdue' },
  { id: 't4', priority: 'urgent', type: 'overdue', icon: '⚠️', title: '48 days without engagement',
    doctor: 'Dr. Deepa Krishnan', spec: 'Gynaecologist', city: 'Kolkata', cat: 'A', score: 38, initials: 'DK',
    action: 'Re-engage Now', hint: 'At-risk status · DMS declining · Immediate attention needed' },
  { id: 't5', priority: 'recommended', type: 'content', icon: '📄', title: 'New SGLT2 paper — interest match',
    doctor: 'Dr. Jayesh Shah', spec: 'Diabetologist', city: 'Hyderabad', cat: 'A+', score: 82, initials: 'JS',
    action: 'Share Paper', hint: 'SGLT2 Inhibitors Meta-Analysis matches his clinical interests in T2DM and SGLT2' },
  { id: 't6', priority: 'recommended', type: 'content', icon: '📄', title: 'New PCOS paper — research match',
    doctor: 'Dr. Kavita Joshi', spec: 'Gynaecologist', city: 'Pune', cat: 'A', score: 76, initials: 'KJ',
    action: 'Share Paper', hint: 'GLP-1 in PCOS study matches her published research interests' },
  { id: 't7', priority: 'recommended', type: 'congratulate', icon: '🏆', title: 'Published a new paper',
    doctor: 'Dr. Kavita Joshi', spec: 'Gynaecologist', city: 'Pune', cat: 'A', score: 76, initials: 'KJ',
    action: 'Send Congratulations', hint: 'Co-authored "PCOS and Hormonal Interventions" — JOGI, March 2026' },
  { id: 't8', priority: 'upcoming', type: 'anniversary', icon: '💍', title: 'Anniversary in 3 days',
    doctor: 'Dr. Arvind Patel', spec: 'Paediatrician', city: 'Ahmedabad', cat: 'A+', score: 79, initials: 'AP',
    action: 'Prepare Wish', hint: '3 May 2026 · Consider sending flowers or a memento via Ferns N Petals' },
  { id: 't9', priority: 'upcoming', type: 'event', icon: '🎓', title: 'Endocrinology CME in 7 days',
    doctor: 'Dr. Madhukar Rai', spec: 'Endocrinologist', city: 'Varanasi', cat: 'A+', score: 76, initials: 'MR',
    action: 'Send CME Invite', hint: 'May 8 CME on insulin resistance — directly relevant to his interests' },
];

const TYPE_CONFIG = {
  birthday:     { bg: '#FEF3C7', color: '#92400E', label: 'Birthday Wish' },
  anniversary:  { bg: 'var(--rose-bg)', color: 'var(--rose)', label: 'Anniversary Wish' },
  content:      { bg: 'var(--purple-bg)', color: 'var(--purple)', label: 'Send Paper' },
  overdue:      { bg: 'var(--red-bg)', color: 'var(--red)', label: 'Re-engage' },
  event:        { bg: 'var(--blue-bg)', color: 'var(--blue)', label: 'CME Invite' },
  congratulate: { bg: 'var(--green-bg)', color: 'var(--green)', label: 'Congratulate' },
};

const PRIORITY_GROUPS = [
  { key: 'urgent',      label: 'Urgent — Do now',       dotColor: 'var(--red)' },
  { key: 'recommended', label: 'Recommended — Do today', dotColor: 'var(--amber)' },
  { key: 'upcoming',    label: 'Upcoming — Plan ahead',  dotColor: 'var(--blue)' },
];

const WISH_MESSAGES = {
  birthday: (name) => `Dear Dr. ${name},\n\nWishing you a very Happy Birthday! 🎂\n\nYour dedication and commitment to your patients is truly inspiring. May this year bring you great joy, good health and every success you deserve.\n\n— Jijo, Team Life · Mankind Pharma`,
  anniversary: (name) => `Dear Dr. ${name},\n\nWarmest congratulations on your Wedding Anniversary! 💍\n\nWishing you and your family a beautiful celebration filled with love and happiness.\n\n— Jijo, Team Life · Mankind Pharma`,
  congratulate: (name) => `Dear Dr. ${name},\n\nHeartfelt congratulations on your recently published paper! 🏆\n\nYour contribution to clinical research is truly remarkable. Very proud to collaborate with such a dedicated clinician.\n\n— Jijo, Team Life · Mankind Pharma`,
};

const MODAL_CONFIG = {
  birthday:     { icon: '🎂', title: 'Birthday Wish', channel: 'WhatsApp' },
  anniversary:  { icon: '💍', title: 'Anniversary Wish', channel: 'WhatsApp' },
  congratulate: { icon: '🏆', title: 'Congratulations', channel: 'WhatsApp' },
  content:      { icon: '📄', title: 'Share Content', channel: 'WhatsApp' },
  overdue:      { icon: '⚠️', title: 'Re-engage Doctor', channel: 'WhatsApp' },
  event:        { icon: '🎓', title: 'Send CME Invite', channel: 'Email' },
};

export default function TodaysTasks() {
  const { addNotification } = useAppContext();
  const [tab, setTab] = useState('all');
  const [doneSet, setDoneSet] = useState(new Set());
  const [activeModal, setActiveModal] = useState(null);
  const [modalMessage, setModalMessage] = useState('');

  const counts = useMemo(() => {
    const active = TASKS.filter(t => !doneSet.has(t.id));
    return {
      all: active.length,
      urgent: active.filter(t => t.priority === 'urgent').length,
      recommended: active.filter(t => t.priority === 'recommended').length,
      upcoming: active.filter(t => t.priority === 'upcoming').length,
      done: doneSet.size,
    };
  }, [doneSet]);

  const filtered = useMemo(() => {
    return TASKS.filter(t => {
      const done = doneSet.has(t.id);
      if (tab === 'done') return done;
      if (done) return false;
      if (tab === 'all') return true;
      return t.priority === tab;
    });
  }, [tab, doneSet]);

  const markDone = (id) => {
    setDoneSet(prev => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
    addNotification('Task marked as done!', 'success');
  };

  const snoozeTask = (id) => {
    setDoneSet(prev => {
      const next = new Set(prev);
      next.add(id);
      return next;
    });
    addNotification('Task snoozed to tomorrow', 'info');
  };

  const openActionModal = (task) => {
    const firstName = task.doctor.replace('Dr. ', '').split(' ')[0];
    const msgFn = WISH_MESSAGES[task.type];
    const defaultMsg = msgFn
      ? msgFn(firstName)
      : `Dear ${task.doctor},\n\nI wanted to reach out regarding ${task.hint}.\n\nLooking forward to connecting with you.\n\n— Jijo, Team Life · Mankind Pharma`;
    setModalMessage(defaultMsg);
    setActiveModal(task);
  };

  const handleSendAction = () => {
    if (!activeModal) return;
    markDone(activeModal.id);
    const config = MODAL_CONFIG[activeModal.type] || { title: 'Action' };
    addNotification(`${config.title} sent to ${activeModal.doctor} via ${config.channel || 'WhatsApp'}`, 'success');
    setActiveModal(null);
    setModalMessage('');
  };

  const total = TASKS.length;
  const doneCount = doneSet.size;
  const progressPct = total > 0 ? (doneCount / total) * 100 : 0;

  const getScoreColor = (score) => score >= 80 ? 'var(--green)' : score >= 50 ? 'var(--amber)' : 'var(--red)';

  const renderTaskCard = (task) => {
    const tc = TYPE_CONFIG[task.type] || { bg: 'var(--surface3)', color: 'var(--text3)', label: 'Act' };
    const stripeClass = task.priority === 'urgent' ? styles.urgentStripe
      : task.priority === 'recommended' ? styles.recommendedStripe
      : styles.upcomingStripe;
    const scoreColor = getScoreColor(task.score);
    const circ = 2 * Math.PI * 11;

    return (
      <div key={task.id} className={`${styles.taskCard} ${stripeClass}`}>
        <div className={styles.taskCardInner}>
          <div className={styles.taskCardLeft}>
            <div className={styles.taskAvatar}>{task.initials}</div>
            <svg width="28" height="28" viewBox="0 0 28 28">
              <circle cx="14" cy="14" r="11" fill="none" stroke="var(--surface3)" strokeWidth="3"/>
              <circle cx="14" cy="14" r="11" fill="none" stroke={scoreColor} strokeWidth="3"
                strokeDasharray={`${circ * (task.score / 100)} ${circ}`}
                strokeDashoffset={circ * 0.25} strokeLinecap="round"
                transform="rotate(-90 14 14)"/>
              <text x="14" y="18" textAnchor="middle" fontFamily="Plus Jakarta Sans" fontSize="7.5" fontWeight="800" fill="var(--navy)">{task.score}</text>
            </svg>
          </div>
          <div className={styles.taskCardBody}>
            <div className={styles.taskBadgeRow}>
              <span className={styles.taskTypeBadge} style={{ background: tc.bg, color: tc.color }}>{tc.label}</span>
              {task.priority === 'urgent' && <span className={styles.urgentTag}>URGENT</span>}
            </div>
            <div className={styles.taskDoctorName}>{task.doctor}</div>
            <div className={styles.taskReason}>{task.spec} · {task.city} · {task.cat} · Score {task.score}</div>
            <div className={styles.taskHint}>{task.hint}</div>
          </div>
          <div className={styles.taskCardRight}>
            <button className={styles.taskPrimaryBtn} onClick={() => openActionModal(task)}>{task.action}</button>
            <div className={styles.taskSecondaryActions}>
              <button className={styles.taskDoneBtn} onClick={() => markDone(task.id)}>Done</button>
              <button className={styles.taskSnoozeBtn} onClick={() => snoozeTask(task.id)}>Tomorrow</button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const tabs = [
    { key: 'all', label: 'All', count: counts.all },
    { key: 'urgent', label: 'Urgent', count: counts.urgent },
    { key: 'recommended', label: 'Recommended', count: counts.recommended },
    { key: 'upcoming', label: 'Upcoming', count: counts.upcoming },
    { key: 'done', label: 'Done', count: counts.done },
  ];

  return (
    <div className={styles.container}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerInner}>
          <div className={styles.headerTop}>
            <div>
              <div className={styles.headerMeta}>Daily Action Centre · Wednesday, 4 May 2026</div>
              <div className={styles.headerGreeting}>Good morning, Jijo <span style={{ color: 'var(--gold2)' }}>👋</span></div>
              <div className={styles.headerSub}>
                {doneCount === total ? 'All tasks done — great work!' : `${total - doneCount} task${total - doneCount !== 1 ? 's' : ''} need attention today`}
              </div>
              <div className={styles.statChips}>
                <div className={styles.statChip}>
                  <div className={styles.statChipValue}>{counts.urgent}</div>
                  <div className={styles.statChipLabel}>Urgent</div>
                </div>
                <div className={styles.statChipDivider} />
                <div className={styles.statChip}>
                  <div className={styles.statChipValue}>{counts.recommended}</div>
                  <div className={styles.statChipLabel}>Recommended</div>
                </div>
                <div className={styles.statChipDivider} />
                <div className={styles.statChip}>
                  <div className={styles.statChipValue}>{counts.upcoming}</div>
                  <div className={styles.statChipLabel}>Upcoming</div>
                </div>
              </div>
            </div>
            <div className={styles.headerScore}>
              <div className={styles.scoreValue}>{doneCount}</div>
              <div className={styles.scoreLabel}>of {total} done</div>
            </div>
          </div>
          <div className={styles.progressTrack}>
            <div className={styles.progressFill} style={{ width: `${progressPct}%` }} />
          </div>
        </div>
      </div>

      {/* Filter tabs */}
      <div className={styles.filterRow}>
        <div className={styles.tabGroup}>
          {tabs.map(t => (
            <button
              key={t.key}
              className={`${styles.tab} ${tab === t.key ? styles.tabActive : ''}`}
              onClick={() => setTab(t.key)}
            >
              {t.label} <span className={styles.tabCount}>{t.count}</span>
            </button>
          ))}
        </div>
        <div className={styles.aiNote}>AI-generated · refreshes daily</div>
      </div>

      {/* Task List */}
      <div className={styles.taskList}>
        {filtered.length === 0 && tab !== 'done' && (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>
              <svg width="40" height="40" viewBox="0 0 40 40" fill="none" stroke="var(--green)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"><path d="M8 20l9 9 15-18"/></svg>
            </div>
            <div className={styles.emptyTitle}>All done for today</div>
            <div className={styles.emptySub}>Great work. Check back tomorrow morning.</div>
          </div>
        )}

        {tab === 'all' ? (
          PRIORITY_GROUPS.map(group => {
            const items = filtered.filter(t => t.priority === group.key);
            if (!items.length) return null;
            return (
              <div key={group.key}>
                <div className={styles.sectionDivider}>
                  <div className={styles.sectionDot} style={{ background: group.dotColor }} />
                  <div className={styles.sectionLabel}>{group.label}</div>
                  <div className={styles.sectionLine} />
                </div>
                {items.map(t => renderTaskCard(t))}
              </div>
            );
          })
        ) : (
          filtered.map(t => renderTaskCard(t))
        )}

        {filtered.length === 0 && tab === 'done' && (
          <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text3)' }}>No tasks completed yet</div>
        )}
      </div>

      {/* Action Modal */}
      {activeModal && (() => {
        const config = MODAL_CONFIG[activeModal.type] || { icon: '💬', title: 'Action', channel: 'WhatsApp' };
        return (
          <div className={styles.modalOverlay} onClick={(e) => { if (e.target === e.currentTarget) setActiveModal(null); }}>
            <div className={styles.modalCard}>
              <div className={styles.modalHeader}>
                <div className={styles.modalHeaderIcon}>{config.icon}</div>
                <div style={{ flex: 1 }}>
                  <div className={styles.modalTitle}>{config.icon} {config.title} · {activeModal.doctor}</div>
                  <div className={styles.modalSub}>{activeModal.spec} · {activeModal.city} · {activeModal.cat} · Score {activeModal.score}</div>
                </div>
                <button className={styles.modalClose} onClick={() => setActiveModal(null)}>✕</button>
              </div>

              <div className={styles.modalBody}>
                <div className={styles.modalLabel}>Channel</div>
                <div className={styles.modalChannel}>
                  <span className={styles.channelBadge} style={{ background: config.channel === 'WhatsApp' ? '#25D366' : '#3B82F6', color: '#fff' }}>
                    {config.channel === 'WhatsApp' ? '💬' : '✉️'} {config.channel}
                  </span>
                </div>

                <div className={styles.modalLabel}>Message Preview</div>
                <textarea
                  className={styles.modalTextarea}
                  value={modalMessage}
                  onChange={(e) => setModalMessage(e.target.value)}
                  rows={8}
                />

                {(activeModal.type === 'birthday' || activeModal.type === 'anniversary') && (
                  <>
                    <div className={styles.modalLabel}>Physical Dispatch (Optional)</div>
                    <div className={styles.giftOptions}>
                      {(activeModal.type === 'birthday'
                        ? [{ icon: '🌸', name: 'Bouquet' }, { icon: '🎂', name: 'Cake' }, { icon: '🏆', name: 'Memento' }]
                        : [{ icon: '🌹', name: 'Bouquet' }, { icon: '🎁', name: 'Gift Box' }, { icon: '🏆', name: 'Memento' }]
                      ).map(g => (
                        <button key={g.name} className={styles.giftBtn}>{g.icon} {g.name}</button>
                      ))}
                    </div>
                  </>
                )}
              </div>

              <div className={styles.modalFooter}>
                <button className={styles.modalCancelBtn} onClick={() => setActiveModal(null)}>Cancel</button>
                <button className={styles.modalSendBtn} onClick={handleSendAction}>
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 7l3.5 3.5 5.5-6.5"/></svg>
                  Send {config.title}
                </button>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}
