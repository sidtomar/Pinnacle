# Business Requirements Document (BRD)
## PinnacleIQ — AI-Powered Medical Content & Field Engagement Platform

| | |
|---|---|
| **Client** | Mankind Pharma |
| **Document Owner** | Product / Engineering |
| **Status** | Draft for review |
| **Version** | 1.1 |
| **Date** | 2026-06-16 |

---

## 1. Executive Summary

PinnacleIQ is a medical content intelligence platform that automates the discovery, summarization, and clinical packaging of medical research, and routes that content through a Medical Affairs (MA) review workflow before Field/Business teams (BU Head / PMT) share it with doctors. It replaces a manual, ad-hoc process of literature search, write-up, and distribution with an AI-agent pipeline plus a structured approval and sharing workflow, backed by doctor relationship intelligence (CRM-style "Doctor 360°" view).

**Problem it solves:** Medical/field teams need a constant stream of credible, India-relevant clinical content to share with doctors to support detailing and engagement — but producing this content manually (literature search → summarization → write-up → compliance review) is slow, inconsistent, and doesn't scale across therapy areas.

**Solution:** A 4-agent AI pipeline (Alpha → Beta → Gamma → Delta) searches medical literature (PubMed + internal MA library), summarizes findings, drafts a clinically-toned article, and packages it into a shareable "content card." Medical Affairs reviews and approves/rejects/requests revisions on each card. Approved cards become available to the Business/Field team, who share them with specific doctors and track engagement.

---

## 2. Business Objectives

| # | Objective | Success Measure |
|---|---|---|
| O1 | Reduce time-to-publish for new medical content | Time from topic selection to MA-approved card (target: minutes, not days) |
| O2 | Ensure all distributed content passes Medical/compliance review | 100% of doctor-facing content has an MA approval record with reviewer name + timestamp |
| O3 | Increase volume & breadth of credible content available to field teams | # of approved content cards per week, per therapy area |
| O4 | Improve relevance of content shared with doctors | Doctor 360° engagement tracking, content-sent history per doctor |
| O5 | Give Medical Affairs full visibility & control over published content | MA review queue, audit trail (versions, rejection reasons, improvement notes) |
| O6 | Give leadership visibility into the funnel (search → approval → sharing → engagement) | Admin Dashboard KPIs, Sharing Reports |

---

## 3. Scope

### 3.1 In Scope
- AI-driven literature search, summarization, article drafting, and content-card generation (4-agent pipeline)
- Medical Affairs review workflow: approve / reject / request improvement / edit metadata
- Content versioning (original + improvement re-runs)
- Doctor database and Doctor 360° profile (overview, CRM intel, content sent history, engagement calendar)
- Content sharing to doctors (WhatsApp/Email delivery stubs) and share-log tracking
- Notifications across roles (new content ready for review, content approved, improvement ready)
- Admin dashboard: pipeline run history, KPIs, scheduler status, doctor data sync, reporting/exports
- Role-based access for three personas: Admin, Medical Affairs, Business User (BU Head/PMT)
- Demo/offline-friendly backend (mock pipeline mode without live LLM calls) for sales/demo use

### 3.2 Out of Scope (current phase)
- Real-time LLM-based production pipeline hardening (currently demo-mode with simulated delays; real LLM path exists but is a separate run mode)
- Live WhatsApp/SendGrid delivery integration (currently stubbed — logs only, no real send unless credentials configured)
- Multi-tenant / multi-company support (single org: Mankind Pharma)
- Mobile native app (web-based SPA only)
- Doctor self-service portal (doctors are managed records, not platform users)

---

## 4. Stakeholders & User Roles

| Role | Who | Primary Goals |
|---|---|---|
| **Admin** | IT/Product admin | Oversee pipeline runs, manage scheduler jobs, sync doctor data, monitor system health, can switch into other roles for testing |
| **Medical Affairs (MA)** | e.g. Dr. Prashant Agarwal | Review AI-generated content for clinical/scientific accuracy and compliance; approve, reject, or request improvements; edit categorization metadata |
| **Business User / BU Head / PMT** | e.g. Jijo | Browse approved content library, find relevant content for specific doctors, share content, track what's been sent and engagement outcomes; export reports |

> **Role note:** "BU Head" and "PMT" refer to the same role/persona in this system — not two separate roles. Medical Affairs (MA) is a distinct role with different permissions (review/approve authority vs. share/export authority).

---

## 5. Current Process vs. Proposed Process

| Step | Current (Manual) | With PinnacleIQ |
|---|---|---|
| Topic/literature discovery | Manual PubMed search by medical writers | Alpha agent auto-searches PubMed + internal MA library per topic |
| Summarization | Manual reading & note-taking | Beta agent auto-summarizes each source into key findings |
| Article drafting | Manual write-up (hours/days) | Gamma agent drafts a 200–500 word clinically-toned article in minutes |
| Content packaging | Manual formatting for distribution | Delta agent generates a structured, taggable content card |
| Compliance/medical review | Ad-hoc, often informal sign-off | Structured MA review queue with approve/reject/improve, reasons & notes captured, full audit trail |
| Distribution to field | Email/WhatsApp manually, no tracking | Tracked share-log per doctor, content-sent history visible in Doctor 360° |
| Reporting | Manual compilation | Admin Dashboard KPIs, CSV/Excel exports, Sharing Report with filters |

---

## 6. Functional Requirements

### 6.1 Research & Content Generation Pipeline
- FR-1: System shall accept a research topic (with specialty/therapy area) and run it through four sequential agents: Alpha (search), Beta (summarize), Gamma (draft article), Delta (package as content card).
- FR-2: Alpha agent shall search PubMed and an internal OneDrive-hosted MA reference library.
- FR-3: Each retrieved paper shall flow independently through Beta → Gamma → Delta, producing one content card per source paper.
- FR-4: System shall support both a "mock" pipeline mode (simulated delays, no LLM cost, for demos) and a "real" pipeline mode (live LLM calls via configurable provider/model).
- FR-5: Generated content cards shall include: title, summary, key findings, clinical insights, recommendations, evidence quality, specialty, therapy area, sub-category, tags, source citations (journal, authors, PMID/DOI, links).
- FR-6: System shall surface pipeline run progress (per-agent status) and allow polling run status by run ID.
- FR-7: System shall maintain a history of past pipeline runs.

### 6.2 Medical Affairs Review Workflow
- FR-8: MA users shall see a queue of content cards in `pending_review` status.
- FR-9: MA shall be able to **approve** a card, recording reviewer name and timestamp; approving must be idempotent (re-approving an already-approved card must not error).
- FR-10: MA shall be able to **reject** a card with a mandatory reason; rejecting an approved card (override) must also be supported.
- FR-11: MA shall be able to **request improvement** on a pending, rejected, or improvement-requested card, with mandatory notes; this triggers a background Beta+Gamma re-run producing a new version linked to the original.
- FR-12: MA shall be able to **edit metadata** (specialty, therapy area, sub-category, tags, summary) independently of approve/reject, via an editable detail view, without needing to re-trigger pipeline logic.
- FR-13: System shall retain version history for any card that has gone through an improvement cycle (original + each revision).
- FR-14: System shall prevent invalid state transitions (e.g., requesting improvement on an already-approved card returns a clear error) while allowing legitimate overrides (e.g., rejecting an approved card).

### 6.3 Content Library
- FR-15: Business Users shall see only `approved` content in their Content Library view.
- FR-16: MA users shall see content across all statuses (pending, approved, rejected, improvement-requested) for review purposes.
- FR-17: Content Library shall support filtering/sorting by specialty, therapy area, tags, and search text.
- FR-18: Each content card shall display distinct, non-duplicated badges for disease/topic vs. specialty vs. therapy area.
- FR-19: On a fresh deployment with no approved content yet, the Business User's Content Library shall be empty (not populated with placeholder/seed data) — approved-only visibility is by design.

### 6.4 Doctor Management & 360° View
- FR-20: System shall maintain a doctor database (name, specialty, location, and related profile attributes).
- FR-21: System shall provide a Doctor 360° view per doctor with four sections: Overview, CRM/relationship intelligence, Content Sent history, and Engagement Calendar.
- FR-22: System shall support syncing doctor data from an external source (Databricks) on demand or on a schedule.

### 6.5 Content Sharing & Engagement
- FR-23: Business Users shall be able to select a doctor and pick approved content to share with them.
- FR-24: System shall log every share event (doctor, content, channel, timestamp) for audit and reporting.
- FR-25: System shall support delivery channel stubs for WhatsApp and Email (real delivery activated only when provider credentials are configured).
- FR-26: System shall support a "Quick Wish" / occasion-based content suggestion flow tied to an Occasion Hub (e.g., festivals, doctor birthdays) to prompt timely outreach.

### 6.6 Notifications
- FR-27: System shall notify Medical Affairs when new content is ready for review.
- FR-28: System shall notify Business Users when content is approved and ready to share.
- FR-29: System shall notify Medical Affairs when an improvement re-run completes.
- FR-30: Users shall be able to mark notifications as read.

### 6.7 Admin & Reporting
- FR-31: Admin shall have a dashboard showing KPIs (e.g., pipeline volume, approval rates, sharing volume) with drill-down detail.
- FR-32: Admin shall be able to view and manually trigger scheduled jobs (daily doctor sync, daily content generation).
- FR-33: System shall provide a Sharing Report with multiple inline filters (e.g., by doctor, specialty, date range, channel).
- FR-34: System shall support exporting Analytics and Sharing Report data as CSV and Excel.
- FR-35: System shall provide a downloadable consolidated report endpoint.

### 6.8 Authentication & Access Control
- FR-36: System shall support login for three roles — Admin, Medical Affairs, Business User — with role-appropriate landing pages and navigation.
- FR-37: Permissions shall be enforced by role: only MA can approve/reject/request improvement; only Business Users (and Admin) can export and share; Admin can switch into other roles for testing/demo purposes.
- FR-38: Session state shall persist across page reloads (client-side session persistence) until explicit sign-out.

---

## 7. End-to-End User Workflows

### 7.1 Content Generation Pipeline Workflow
1. User (Admin or MA) selects a research topic, specialty, and therapy area in the Research Agent screen and clicks **Run Pipeline**.
2. Frontend calls `POST /pipeline/run`; backend creates a run record and starts the Alpha → Beta → Gamma → Delta sequence (real or mock mode) as a background task, returning a `run_id` immediately.
3. Frontend polls `GET /pipeline/status/{run_id}` every 2 seconds (`plPoll()` in `PinnacleIQ_Portal.html`) and updates a 4-stage progress visualization (Alpha/Beta/Gamma/Delta) as each agent completes.
4. Each paper Alpha finds flows independently through Beta → Gamma → Delta, producing one content card per source paper, saved with status `pending_review`.
5. Polling stops once the run status reports completion; newly created cards become visible in the MA review queue.

### 7.2 Medical Affairs Review Workflow
1. MA opens the review queue, which lists all cards in `pending_review` (plus `rejected` / `improvement_requested` for visibility).
2. **Approve**: MA clicks Approve → `POST /content/{id}/approve` with `reviewer` name. Status becomes `approved`. Re-approving an already-approved card is a no-op (idempotent, no duplicate notification). On first transition into `approved`, a notification is sent to BU Head (`notify_bu_content_approved`).
3. **Reject**: MA clicks Reject and must supply a reason → `POST /content/{id}/reject`. Status becomes `rejected`, reason stored. Rejecting an already-approved card (override) is permitted. After a successful reject, the UI shows a "send to agents" prompt (`_showSendToAgentsPrompt`) offering to immediately request an improvement using the rejection reason as the improvement notes — tying reject directly into the next workflow.
4. **Request Improvement**: MA supplies mandatory notes → `POST /content/{id}/improve`. Allowed from `pending_review`, `rejected`, or `improvement_requested` (not from `approved` — returns 400). Status becomes `improvement_requested`; a background Beta+Gamma re-run is kicked off and a `run_id` returned for polling `/pipeline/status/{run_id}` (same polling mechanism as 7.1). On completion, MA is notified the improvement is ready, and a new versioned card is linked to the original.
5. **Edit Metadata**: MA can independently edit specialty, therapy area, sub-category, tags, and summary via `PATCH /content/{id}` without affecting status or triggering any pipeline re-run ("Save Changes" in the card detail view).

### 7.3 Content Sharing Workflow
1. BU Head/PMT opens Content Library (approved-only view) or a Doctor 360° profile.
2. Selects one or more approved content cards and a target doctor.
3. Chooses a delivery channel (WhatsApp or Email — stubbed unless provider credentials are configured) and shares.
4. Backend logs the share event (doctor, content, channel, timestamp) — visible afterward in the doctor's Content Sent history and in the Sharing Report.

---

## 8. Download & Report Formats

### 8.1 Business Report (Excel) — `GET /report/download`
- Triggered from the Admin Dashboard "Download Report" button (`downloadExcelReport()`); currently called without filter params from the UI even though the endpoint accepts them.
- Backend: `report_generator.generate_business_report(items, search_params)` in `demo/backend/report_generator.py`.
- Optional query filters supported by the endpoint: `status`, `specialty`, `therapy_area`, `disease`, `keywords`, `date_from`, `date_to`. Returns 404 if no items match.
- File name: `PinnacleIQ_PubMed_Database_{YYYY-MM-DD}.xlsx` (date = generation date, UTC).
- **Actual workbook structure (2 sheets)** — note the module docstring describes an additional "All Publications" + per-specialty tab structure, but `generate_business_report()` does not call those helper functions; only the two sheets below are produced today:
  1. **"Search Summary"** — key/value rows: Generated on, Therapy Area, Disease, Keywords, Date From, Date To, Total Articles.
  2. **"PubMed Research Database"** — styled table (navy title bar, yellow column headers, alternating row shading, frozen header row, hyperlinked PubMed/DOI columns) with 15 columns in order:
     `#`, `Date`, `Specialty`, `Therapy Area`, `Sub-category`, `Tags`, `Relevant Doctor Specialties`, `WhatsApp Summary`, `Title`, `PMID`, `DOI`, `Abstract` (mapped from the card's `summary` field), `Authors`, `PubMed Link`, `Full Text Link (DOI)`.

### 8.2 Sharing Report (CSV) — client-side export
- Triggered from the Sharing Report screen (`exportSharingReport()`).
- Builds a CSV from `SR_DATA` and triggers a real browser file download (Blob).
- File name: `PinnacleIQ_SharingReport_{YYYY-MM-DD}.csv`.
- Columns (9): `S.No`, `Article Title`, `Creation Date`, `Review Date`, `Shared Date`, `Doctor Name`, `Specialty`, `Channel`, `Shared By`.

### 8.3 Analytics Export (CSV — clipboard only)
- Triggered from the Analytics screen (`exportAnalyticsCSV()`).
- Builds a CSV from the doctor dataset but **copies it to the clipboard only** (`navigator.clipboard.writeText`) — it does **not** download a file. Toast confirms "Exported N rows to clipboard (CSV)".
- **Important UX distinction**: unlike the Sharing Report export, this is not a downloadable artifact; users must paste the clipboard contents elsewhere (e.g. Excel) themselves.

---

## 9. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Performance** | Pipeline run status must be pollable without blocking the UI; content list/filter operations should respond within a few seconds for current data volumes (~100s of cards) |
| **Reliability** | Approve/reject/improve operations must be idempotent or fail safely; a transient error in a side-effect (e.g., notification) must not corrupt or block the primary state change |
| **Internationalization / Encoding** | All user-facing and stored text must be handled as UTF-8 end-to-end (server console, database, API responses) to avoid corruption or crashes on non-ASCII characters (e.g., em-dashes in titles) |
| **Auditability** | Every approval, rejection, and improvement request must capture reviewer identity, timestamp, and (for reject/improve) a reason/notes field |
| **Availability** | Demo/offline mode must allow the full UI to be exercised without dependency on live LLM or external API keys |
| **Data Residency** | Production data store (Databricks) vs. local demo store (SQLite) must be switchable via configuration without code changes |
| **Usability** | Distinct, role-appropriate navigation; clear visual status indication (badges/colors) for content review state |
| **Maintainability** | Storage and LLM provider must be abstracted behind factory interfaces so backend can switch providers/stores via environment configuration only |

---

## 10. Assumptions & Constraints

- Single deployment serves one organization (Mankind Pharma); no multi-tenancy.
- The React frontend codebase in the repository is legacy/unused; the single-file HTML portal is the actual product UI.
- Real-money/production LLM calls require API keys (OpenRouter) and are out of scope for the always-available demo experience.
- WhatsApp/Email delivery requires third-party credentials (Twilio/SendGrid) not provisioned by default; until then, sends are logged stubs.
- The system currently runs as a single-instance FastAPI service with a local SQLite store in demo mode; horizontal scaling and concurrent-write handling under load have not been load-tested.

---

## 11. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| AI-generated clinical content contains inaccuracies | High — regulatory/reputational | Mandatory MA review gate before any content reaches doctors; no auto-publish path exists |
| Encoding/locale issues crash server-side notification logic | Medium — false error states, support burden | Enforce UTF-8 across server startup, logging, and printing (fix already identified and applied to startup script) |
| SQLite concurrency limits under multi-user production load | Medium | Databricks-backed production store is the designed scale-out path; should be validated under realistic concurrent load before go-live |
| Stubbed delivery channels give false impression of "sent" content | Medium | Clear UI/reporting distinction between "shared in-app" vs. "delivered via WhatsApp/Email" once real integrations are enabled |
| Content Library appears empty to Business Users on first deployment | Low — by design, but may confuse new users without explanation | Add onboarding messaging explaining the approve-first gating behavior |

---

## 12. Glossary

| Term | Meaning |
|---|---|
| **MA** | Medical Affairs — the review/approval role |
| **BU Head / PMT** | Business Unit Head / Product Management Team — the field-facing sharing role (same person/role) |
| **Alpha / Beta / Gamma / Delta** | The four sequential AI agents in the content pipeline (search, summarize, draft, package) |
| **Content Card** | A structured, packaged unit of medical content output by the Delta agent, subject to MA review |
| **Pending Review** | Content card status awaiting MA decision |
| **Improvement Requested** | Content card status indicating MA asked for a revision; triggers a Beta+Gamma re-run |
| **Content Library** | The browsable collection of content cards (scope varies by role) |
| **Doctor 360°** | The consolidated profile view of a single doctor across overview, CRM intel, content history, and engagement |
| **Occasion Hub** | Feature surfacing timely outreach opportunities (festivals, doctor milestones) |

---

## 13. Open Questions for Stakeholder Sign-off

1. What is the target SLA for MA review turnaround once a card enters `pending_review`?
2. Should there be a maximum number of pending/unreviewed cards before pipeline runs are throttled?
3. Is there a compliance requirement to retain rejected content and rejection reasons for a minimum period (e.g., regulatory audit)?
4. When real WhatsApp/Email delivery is enabled, who owns the sender identity/compliance approval for outbound messages to doctors?
5. Is multi-tenancy (supporting other pharma brands/divisions) a near-term roadmap item, or confirmed out of scope long-term?
