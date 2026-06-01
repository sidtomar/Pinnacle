"""
PinnacleIQ Demo Backend
========================
FastAPI server for the management demo.

Storage backend is configured via STORE_BACKEND env var:
  STORE_BACKEND=sqlite       <- default for demo (zero setup)
  STORE_BACKEND=databricks   <- production (after management approval)

The API code never touches SQLite or Databricks directly —
it only calls the store abstraction. So migration = one env var change.
"""
import sys, os, json

# Allow importing from research_agent_system/store/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research_agent_system"))

import threading
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from store import get_store
from mock_runner import run_mock_pipeline
from notifications import notify_ma_new_content, notify_ma_improvement_ready, notify_bu_content_approved
from improvement_runner import run_improvement_pipeline
from doctor_sync import sync_doctors, get_sync_status
from report_generator import generate_business_report
import scheduler as sched

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="PinnacleIQ Research API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
TOPICS_FILE   = Path(__file__).parent.parent / "topics.txt"
DOCTORS_FILE  = Path(__file__).parent.parent / "doctors.json"

# ── Initialise store on startup ───────────────────────────────────────────────
# get_store() reads STORE_BACKEND env var -> returns SQLiteStore or DatabricksStore
# setup() creates tables if they don't exist (idempotent)
store = get_store()
store.setup()

# Start daily job scheduler (gracefully skips if apscheduler not installed)
try:
    sched.start_scheduler(
        sync_hour=int(os.getenv("SYNC_HOUR", "6")),
        sync_minute=int(os.getenv("SYNC_MINUTE", "30")),
        content_hour=int(os.getenv("CONTENT_HOUR", "7")),
        content_minute=int(os.getenv("CONTENT_MINUTE", "0")),
    )
except Exception as e:
    print(f"[App] Scheduler start failed: {e}")

# In-memory pipeline run status (transient — doesn't need persistence)
pipeline_runs: dict = {}
_lock = threading.Lock()

# ── Pydantic schemas ──────────────────────────────────────────────────────────
class RunRequest(BaseModel):
    topic: str
    specialty: str
    therapy_area: str

class ApproveRequest(BaseModel):
    reviewer: Optional[str] = "Dr. Prashant Agarwal (MA)"

class RejectRequest(BaseModel):
    reason: str
    reviewer: Optional[str] = "Dr. Prashant Agarwal (MA)"

class ShareRequest(BaseModel):
    doctor_id:    Optional[str] = "doc_001"
    doctor_name:  Optional[str] = "Demo Doctor"
    specialty:    Optional[str] = "General Medicine"
    channel:      Optional[str] = "whatsapp"
    shared_by:    Optional[str] = "Jijo (BU Head · PMT)"

class ImprovementRequest(BaseModel):
    notes: str
    reviewer: Optional[str] = "Dr. Prashant Agarwal (MA)"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    backend = os.getenv("STORE_BACKEND", "sqlite")
    return {"status": "ok", "service": "PinnacleIQ Research API", "store": backend}


@app.get("/doctors")
def get_doctors(
    specialty: Optional[str] = None,
    city:      Optional[str] = None,
    tier:      Optional[str] = None,
    channel:   Optional[str] = None,
    q:         Optional[str] = None,       # free-text search on name / hospital
):
    """
    Return the doctor training database (100 doctors, 10 specialties).
    Filters: specialty, city, tier (A/B/C), channel (whatsapp/email), q (name search).
    Replace DOCTORS_FILE source with Databricks query once post-approval sync is live.
    """
    if not DOCTORS_FILE.exists():
        raise HTTPException(404, "doctors.json not found — run demo/generate_doctors.py first")
    data = json.loads(DOCTORS_FILE.read_text(encoding="utf-8"))
    docs = data.get("doctors", [])

    if specialty:
        docs = [d for d in docs if d["specialty"].lower() == specialty.lower()]
    if city:
        docs = [d for d in docs if d["city"].lower() == city.lower()]
    if tier:
        docs = [d for d in docs if d["tier"].upper() == tier.upper()]
    if channel:
        docs = [d for d in docs if d["preferred_channel"].lower() == channel.lower()]
    if q:
        q_lower = q.lower()
        docs = [d for d in docs if q_lower in d["name"].lower() or q_lower in d["hospital"].lower()]

    return {
        "total":      len(docs),
        "filters":    {"specialty": specialty, "city": city, "tier": tier, "channel": channel, "q": q},
        "doctors":    docs,
        "meta":       {"generated_at": data.get("generated_at"), "specialties": data.get("specialties"), "cities": data.get("cities"), "tier_breakdown": data.get("tier_breakdown")},
    }


@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: str):
    """Return a single doctor by ID (e.g. DOC001)."""
    if not DOCTORS_FILE.exists():
        raise HTTPException(404, "doctors.json not found")
    data = json.loads(DOCTORS_FILE.read_text(encoding="utf-8"))
    doc = next((d for d in data["doctors"] if d["id"] == doctor_id.upper()), None)
    if not doc:
        raise HTTPException(404, f"Doctor {doctor_id} not found")
    return doc


@app.get("/topics")
def get_topics():
    """Read research topics from topics.txt."""
    if not TOPICS_FILE.exists():
        raise HTTPException(404, f"topics.txt not found at {TOPICS_FILE}")
    topics = []
    for line in TOPICS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        topics.append({
            "topic":        parts[0] if len(parts) > 0 else line,
            "specialty":    parts[1] if len(parts) > 1 else "General Medicine",
            "therapy_area": parts[2] if len(parts) > 2 else "General",
        })
    return {"topics": topics, "count": len(topics)}


@app.post("/pipeline/run")
def start_pipeline(req: RunRequest, bg: BackgroundTasks):
    """Start mock pipeline in background. Returns run_id for polling."""
    from datetime import datetime, timezone
    run_id = str(uuid.uuid4())
    with _lock:
        pipeline_runs[run_id] = {
            "status":        "running",
            "topic":         req.topic,
            "specialty":     req.specialty,
            "progress":      0,
            "current_agent": "alpha",
            "status_msg":    "Starting pipeline...",
            "content_id":    None,
            "improvement":   False,
            "started_at":    datetime.now(timezone.utc).isoformat(),
        }

    def _run():
        run_mock_pipeline(
            topic=req.topic,
            specialty=req.specialty,
            therapy_area=req.therapy_area,
            run_store=pipeline_runs,
            run_id=run_id,
        )
        # Persist completed content via the store abstraction
        # Save ALL cards (one per paper) to SQLite
        run = pipeline_runs.get(run_id, {})
        if run.get("status") == "completed":
            all_cards = run.get("all_cards", [])
            if not all_cards and run.get("content"):
                all_cards = [run["content"]]  # backward compat: single card

            saved_ids = []
            for card in all_cards:
                try:
                    cid = store.save_content_card(card)
                    saved_ids.append(cid)
                    print(f"[App] Saved card: {card.get('title','')[:60]}... → {cid}")
                except Exception as e:
                    print(f"[App] Failed to save card: {e}")

            pipeline_runs[run_id]["content_id"] = saved_ids[0] if saved_ids else None
            pipeline_runs[run_id]["all_content_ids"] = saved_ids
            print(f"[App] Pipeline saved {len(saved_ids)} card(s) to SQLite")

            # Notify MA team that new content is ready for review
            try:
                first_card = all_cards[0] if all_cards else run.get("content", {})
                notify_ma_new_content(
                    store,
                    saved_ids[0] if saved_ids else "",
                    first_card.get("title", req.topic),
                    req.specialty,
                    first_card.get("division", "All"),
                )
            except Exception as e:
                print(f"[App] Pipeline notification failed: {e}")

    bg.add_task(_run)
    return {"run_id": run_id, "status": "running"}


@app.get("/pipeline/status/{run_id}")
def pipeline_status(run_id: str):
    """Poll for pipeline progress (0-100%)."""
    run = pipeline_runs.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return {
        "run_id":         run_id,
        "status":         run["status"],
        "progress":       run["progress"],
        "current_agent":  run["current_agent"],
        "status_msg":     run["status_msg"],
        "content_id":     run.get("content_id"),
        "all_content_ids": run.get("all_content_ids", []),
        "agent_outputs":  run.get("agent_outputs", {}),
    }


@app.get("/pipeline/runs")
def get_pipeline_runs(limit: int = 30):
    """
    Return recent pipeline runs — both new research runs and improvement re-runs.
    Used by the Research Pipeline page to show activity history.
    """
    runs = []
    for run_id, run in pipeline_runs.items():
        runs.append({
            "run_id":        run_id,
            "type":          "improvement" if run.get("improvement") else "new",
            "topic":         run.get("topic", "Unknown"),
            "specialty":     run.get("specialty", ""),
            "status":        run.get("status", "unknown"),
            "progress":      run.get("progress", 0),
            "current_agent": run.get("current_agent", ""),
            "status_msg":    run.get("status_msg", ""),
            "content_id":    run.get("content_id"),
            "original_id":   run.get("original_id"),
            "version":       run.get("version"),
            "started_at":    run.get("started_at", ""),
        })
    # Most recent first (insertion order reversed)
    runs.reverse()
    return {"runs": runs[:limit], "total": len(runs)}


@app.get("/content")
def list_content(status: Optional[str] = None, specialty: Optional[str] = None):
    """List all content items with optional filters."""
    items = store.list_content(status=status, specialty=specialty)
    return {
        "items": items,
        "counts": {
            "total":    len(items),
            "pending":  sum(1 for i in items if i.get("status") == "pending_review"),
            "approved": sum(1 for i in items if i.get("status") == "approved"),
            "rejected": sum(1 for i in items if i.get("status") == "rejected"),
        },
    }


@app.get("/content/{content_id}")
def get_content(content_id: str):
    """Get a single content item."""
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    return item


@app.post("/content/{content_id}/approve")
def approve_content(content_id: str, req: ApproveRequest):
    """MA approves a content card."""
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    if item.get("status") not in ("pending_review", "improvement_requested"):
        raise HTTPException(400, f"Content is already '{item.get('status')}'")
    store.approve(content_id, reviewer=req.reviewer)
    # Notify BU Head that content is approved and ready to share
    try:
        notify_bu_content_approved(
            store,
            content_id,
            item.get("title", content_id),
            item.get("division", "All"),
        )
    except Exception as e:
        print(f"[App] Approval notification failed: {e}")
    return {"message": "Content approved. Now available for BU Head to share.", "content_id": content_id}


@app.post("/content/{content_id}/reject")
def reject_content(content_id: str, req: RejectRequest):
    """MA rejects a content card with a reason."""
    if not req.reason.strip():
        raise HTTPException(400, "Rejection reason is required")
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    store.reject(content_id, reason=req.reason, reviewer=req.reviewer)
    return {"message": "Content rejected.", "content_id": content_id}


@app.post("/content/{content_id}/share")
def share_content(content_id: str, req: ShareRequest):
    """BU Head shares content with a doctor.
    Note: approval check removed — sharing and MA approval are independent workflows.
    PMT can share any pipeline-generated content.
    Accepts both API-sourced (UUID) and static (static-N) content IDs."""
    result = store.log_share(
        content_id=content_id,
        doctor_id=req.doctor_id,
        doctor_name=req.doctor_name,
        doctor_specialty=req.specialty,
        channel=req.channel,
        shared_by=req.shared_by,
    )
    return {
        "message": f"Content shared via {req.channel} with {req.doctor_name}.",
        "log_id":  result["log_id"],
        "warning": result["warning"],
    }


@app.get("/share-logs")
def get_share_logs(content_id: Optional[str] = None):
    """Return sharing history."""
    return {"logs": store.get_share_logs(content_id=content_id)}


# ── Improvement (HITL) endpoints ──────────────────────────────────────────────

@app.post("/content/{content_id}/request-improvement")
def request_improvement(content_id: str, req: ImprovementRequest, bg: BackgroundTasks):
    """
    MA requests improvement on a content card.
    Sets status to 'improvement_requested', then runs Beta+Gamma re-run in background.
    Returns run_id for polling via /pipeline/status/{run_id}.
    """
    if not req.notes or not req.notes.strip():
        raise HTTPException(400, "Improvement notes are required")

    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    # Allow improvement on pending_review, improvement_requested, AND rejected content
    if item.get("status") not in ("pending_review", "improvement_requested", "rejected"):
        raise HTTPException(400, f"Content status is '{item.get('status')}' — cannot request improvement")

    # Mark as improvement_requested in the DB
    store.request_improvement(content_id, notes=req.notes, reviewer=req.reviewer)

    # Start improvement pipeline in background
    from datetime import datetime, timezone
    run_id = str(uuid.uuid4())
    with _lock:
        pipeline_runs[run_id] = {
            "status":        "running",
            "topic":         item.get("topic", ""),
            "specialty":     item.get("specialty", ""),
            "progress":      0,
            "current_agent": "alpha",
            "status_msg":    "Starting improvement pipeline...",
            "content_id":    None,
            "improvement":   True,
            "original_id":   content_id,
            "started_at":    datetime.now(timezone.utc).isoformat(),
        }

    def _run_improvement():
        run_improvement_pipeline(
            original_content=item,
            improvement_notes=req.notes,
            run_store=pipeline_runs,
            run_id=run_id,
            store=store,
            notify_fn=notify_ma_improvement_ready,
        )

    bg.add_task(_run_improvement)
    return {
        "run_id":      run_id,
        "status":      "running",
        "message":     "Improvement pipeline started. Poll /pipeline/status/{run_id} for progress.",
        "content_id":  content_id,
    }


@app.get("/content/{content_id}/versions")
def get_content_versions(content_id: str):
    """Return all versions of a content card (original + improvements)."""
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    # Resolve root ID — if this card is itself a revision, find the root
    root_id = item.get("parent_id") or content_id
    versions = store.get_content_versions(root_id)
    return {
        "root_id":  root_id,
        "versions": versions,
        "count":    len(versions),
    }


# ── Notification endpoints ────────────────────────────────────────────────────

@app.get("/notifications")
def get_notifications(
    division: Optional[str] = None,
    unread_only: bool = False,
):
    """Return in-app notifications, optionally filtered by division or unread status."""
    notifications = store.get_notifications(division=division, unread_only=unread_only)
    unread_count = sum(1 for n in notifications if not n.get("read_at"))
    return {
        "notifications": notifications,
        "total":         len(notifications),
        "unread":        unread_count,
    }


@app.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str):
    """Mark a notification as read."""
    store.mark_notification_read(notification_id)
    return {"message": "Notification marked as read", "notification_id": notification_id}


# ── Scheduler endpoints ───────────────────────────────────────────────────────

@app.get("/scheduler/status")
def scheduler_status():
    """Return the scheduler running state and list of scheduled jobs."""
    return {
        **sched.get_scheduler_status(),
        "job_history": sched.get_job_history()[:10],  # last 10 entries
    }


@app.post("/scheduler/run-now/{job_name}")
def run_job_now(job_name: str):
    """Manually trigger a scheduled job immediately (doctor_sync or content_generation)."""
    result = sched.run_job_now(job_name)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return {"message": f"Job '{job_name}' triggered in background", **result}


# ── Doctor sync endpoint ──────────────────────────────────────────────────────

@app.post("/sync/doctors")
def sync_doctors_endpoint(division: Optional[str] = None):
    """
    Manual doctor sync trigger.
    Pulls from Databricks Superman CRM table (or falls back to JSON cache in demo mode).
    """
    result = sync_doctors(division_filter=division)
    return {
        "message":      f"Doctor sync complete — {result['count']} doctors loaded",
        "count":        result["count"],
        "source":       result["source"],
        "duration_sec": result.get("duration_sec", 0),
        "sync_status":  get_sync_status(),
    }


@app.get("/sync/doctors/status")
def doctor_sync_status():
    """Return the last doctor sync status."""
    return get_sync_status()



# ── Business Report ──────────────────────────────────────────────────────────

@app.get("/report/download")
def download_business_report(
    status: Optional[str] = None,
    specialty: Optional[str] = None,
):
    """
    Generate and download the PinnacleIQ Business Report as an Excel file.
    Optional filters: status (approved, pending_review, etc.), specialty.
    """
    from datetime import datetime, timezone

    items = store.list_content(status=status, specialty=specialty, limit=10000)
    if not items:
        raise HTTPException(404, "No content items found for the given filters.")

    buf = generate_business_report(items)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"PinnacleIQ_PubMed_Repository_{date_str}.xlsx"

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


if __name__ == "__main__":
    import uvicorn
    import sys
    port = int(sys.argv[sys.argv.index("--port") + 1]) if "--port" in sys.argv else 8010
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
