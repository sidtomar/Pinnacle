"""
PinnacleIQ Demo Backend
========================
FastAPI server for the management demo.

Storage backend is configured via STORE_BACKEND env var:
  STORE_BACKEND=sqlite       ← default for demo (zero setup)
  STORE_BACKEND=databricks   ← production (after management approval)

The API code never touches SQLite or Databricks directly —
it only calls the store abstraction. So migration = one env var change.
"""
import sys, os

# Allow importing from research_agent_system/store/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research_agent_system"))

import threading
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from store import get_store
from mock_runner import run_mock_pipeline

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="PinnacleIQ Research API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from pathlib import Path
TOPICS_FILE = Path(__file__).parent.parent / "topics.txt"

# ── Initialise store on startup ───────────────────────────────────────────────
# get_store() reads STORE_BACKEND env var → returns SQLiteStore or DatabricksStore
# setup() creates tables if they don't exist (idempotent)
store = get_store()
store.setup()

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


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    backend = os.getenv("STORE_BACKEND", "sqlite")
    return {"status": "ok", "service": "PinnacleIQ Research API", "store": backend}


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
    run_id = str(uuid.uuid4())
    with _lock:
        pipeline_runs[run_id] = {
            "status":        "running",
            "topic":         req.topic,
            "progress":      0,
            "current_agent": "alpha",
            "status_msg":    "Starting pipeline...",
            "content_id":    None,
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
        run = pipeline_runs.get(run_id, {})
        if run.get("status") == "completed" and run.get("content"):
            content_id = store.save_content_card(run["content"])
            pipeline_runs[run_id]["content_id"] = content_id

    bg.add_task(_run)
    return {"run_id": run_id, "status": "running"}


@app.get("/pipeline/status/{run_id}")
def pipeline_status(run_id: str):
    """Poll for pipeline progress (0-100%)."""
    run = pipeline_runs.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return {
        "run_id":        run_id,
        "status":        run["status"],
        "progress":      run["progress"],
        "current_agent": run["current_agent"],
        "status_msg":    run["status_msg"],
        "content_id":    run.get("content_id"),
    }


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
    if item.get("status") != "pending_review":
        raise HTTPException(400, f"Content is already '{item.get('status')}'")
    store.approve(content_id, reviewer=req.reviewer)
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
    """BU Head shares approved content with a doctor."""
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    if item.get("status") != "approved":
        raise HTTPException(400, "Content must be approved before sharing")

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
