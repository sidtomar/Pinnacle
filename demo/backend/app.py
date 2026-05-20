"""
PinnacleIQ Demo Backend
FastAPI + SQLite — reads topics from topics.txt, runs mock pipeline,
stores content for MA review and BU Head sharing.
"""
import json, sqlite3, threading, uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from mock_runner import run_mock_pipeline

# ── App setup ────────────────────────────────────────────────────────────────
app = FastAPI(title="PinnacleIQ Research API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

BASE = Path(__file__).parent
DB_PATH = BASE / "pinnacleiq.db"
TOPICS_FILE = BASE.parent / "topics.txt"

# In-memory store for pipeline run status (no DB needed for transient state)
pipeline_runs: dict = {}
_lock = threading.Lock()

# ── Database ─────────────────────────────────────────────────────────────────
def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS content_items (
            id              TEXT PRIMARY KEY,
            topic           TEXT NOT NULL,
            title           TEXT NOT NULL,
            specialty       TEXT,
            therapy_area    TEXT,
            sub_category    TEXT,
            tags            TEXT,         -- JSON array
            summary         TEXT,
            key_findings    TEXT,         -- JSON array
            clinical_insights TEXT,
            recommendations TEXT,         -- JSON array
            emerging_trends TEXT,         -- JSON array
            short_article   TEXT,
            full_research   TEXT,
            evidence_quality TEXT,
            status          TEXT DEFAULT 'pending_review',
            rejection_reason TEXT,
            created_at      TEXT,
            reviewed_at     TEXT,
            source          TEXT DEFAULT 'ai_agent'
        );

        CREATE TABLE IF NOT EXISTS share_logs (
            id          TEXT PRIMARY KEY,
            content_id  TEXT NOT NULL,
            doctor_id   TEXT,
            doctor_name TEXT,
            channel     TEXT,
            shared_at   TEXT,
            shared_by   TEXT
        );
    """)
    conn.commit()
    conn.close()

init_db()

# ── Helpers ──────────────────────────────────────────────────────────────────
def row_to_dict(row) -> dict:
    d = dict(row)
    for field in ("tags", "key_findings", "recommendations", "emerging_trends"):
        if d.get(field) and isinstance(d[field], str):
            try:
                d[field] = json.loads(d[field])
            except Exception:
                d[field] = []
    return d

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

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
    doctor_id: Optional[str] = "doc_001"
    doctor_name: Optional[str] = "Demo Doctor"
    channel: Optional[str] = "whatsapp"
    shared_by: Optional[str] = "Jijo (BU Head · PMT)"

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    return {"status": "ok", "service": "PinnacleIQ Research API"}


# ── Topics ────────────────────────────────────────────────────────────────────
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
            "topic":       parts[0] if len(parts) > 0 else line,
            "specialty":   parts[1] if len(parts) > 1 else "General Medicine",
            "therapy_area": parts[2] if len(parts) > 2 else "General",
        })
    return {"topics": topics, "count": len(topics)}


# ── Pipeline ──────────────────────────────────────────────────────────────────
@app.post("/pipeline/run")
def start_pipeline(req: RunRequest, bg: BackgroundTasks):
    """Trigger the research pipeline for a topic. Returns a run_id for polling."""
    run_id = str(uuid.uuid4())
    with _lock:
        pipeline_runs[run_id] = {
            "status":       "running",
            "topic":        req.topic,
            "specialty":    req.specialty,
            "therapy_area": req.therapy_area,
            "progress":     0,
            "current_agent": "alpha",
            "status_msg":   "Starting pipeline...",
            "content":      None,
            "content_id":   None,
            "started_at":   now_iso(),
        }

    def _run():
        run_mock_pipeline(
            topic=req.topic,
            specialty=req.specialty,
            therapy_area=req.therapy_area,
            run_store=pipeline_runs,
            run_id=run_id,
        )
        # Persist to DB once complete
        run = pipeline_runs.get(run_id, {})
        if run.get("status") == "completed" and run.get("content"):
            c = run["content"]
            cid = str(uuid.uuid4())
            conn = get_db()
            conn.execute(
                """INSERT INTO content_items
                   (id, topic, title, specialty, therapy_area, sub_category,
                    tags, summary, key_findings, clinical_insights,
                    recommendations, emerging_trends, short_article,
                    evidence_quality, status, created_at, source)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    cid,
                    c.get("topic", req.topic),
                    c.get("title", ""),
                    c.get("specialty", req.specialty),
                    c.get("therapy_area", req.therapy_area),
                    c.get("sub_category", "Review Article"),
                    json.dumps(c.get("tags", [])),
                    c.get("summary", ""),
                    json.dumps(c.get("key_findings", [])),
                    c.get("clinical_insights", ""),
                    json.dumps(c.get("recommendations", [])),
                    json.dumps(c.get("emerging_trends", [])),
                    c.get("short_article", ""),
                    c.get("evidence_quality", ""),
                    "pending_review",
                    now_iso(),
                    "ai_agent",
                ),
            )
            conn.commit()
            conn.close()
            pipeline_runs[run_id]["content_id"] = cid

    bg.add_task(_run)
    return {"run_id": run_id, "status": "running"}


@app.get("/pipeline/status/{run_id}")
def pipeline_status(run_id: str):
    """Poll for pipeline run progress."""
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


# ── Content Library ───────────────────────────────────────────────────────────
@app.get("/content")
def list_content(status: Optional[str] = None):
    """List all content items (optionally filtered by status)."""
    conn = get_db()
    if status:
        rows = conn.execute(
            "SELECT * FROM content_items WHERE status=? ORDER BY created_at DESC",
            (status,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM content_items ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    items = [row_to_dict(r) for r in rows]
    return {
        "items": items,
        "counts": {
            "total": len(items),
            "pending": sum(1 for i in items if i["status"] == "pending_review"),
            "approved": sum(1 for i in items if i["status"] == "approved"),
            "rejected": sum(1 for i in items if i["status"] == "rejected"),
        }
    }


@app.get("/content/{content_id}")
def get_content(content_id: str):
    """Get a single content item."""
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM content_items WHERE id=?", (content_id,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Content not found")
    return row_to_dict(row)


@app.post("/content/{content_id}/approve")
def approve_content(content_id: str, req: ApproveRequest):
    """MA approves a content item."""
    conn = get_db()
    row = conn.execute("SELECT status FROM content_items WHERE id=?", (content_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Content not found")
    if row["status"] != "pending_review":
        conn.close()
        raise HTTPException(400, f"Content is already '{row['status']}'")
    conn.execute(
        "UPDATE content_items SET status='approved', reviewed_at=? WHERE id=?",
        (now_iso(), content_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Content approved. Now available for BU Head to share.", "content_id": content_id}


@app.post("/content/{content_id}/reject")
def reject_content(content_id: str, req: RejectRequest):
    """MA rejects a content item with a reason."""
    if not req.reason.strip():
        raise HTTPException(400, "Rejection reason is required")
    conn = get_db()
    row = conn.execute("SELECT status FROM content_items WHERE id=?", (content_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Content not found")
    conn.execute(
        "UPDATE content_items SET status='rejected', rejection_reason=?, reviewed_at=? WHERE id=?",
        (req.reason, now_iso(), content_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Content rejected.", "content_id": content_id}


@app.post("/content/{content_id}/share")
def share_content(content_id: str, req: ShareRequest):
    """BU Head shares approved content with a doctor (with 30-day frequency check)."""
    conn = get_db()

    # Check content exists and is approved
    row = conn.execute("SELECT status, title FROM content_items WHERE id=?", (content_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(404, "Content not found")
    if row["status"] != "approved":
        conn.close()
        raise HTTPException(400, "Content must be approved before sharing")

    # 30-day frequency check
    recent = conn.execute(
        """SELECT COUNT(*) as cnt FROM share_logs
           WHERE doctor_id=? AND shared_at > datetime('now','-30 days')""",
        (req.doctor_id,)
    ).fetchone()
    warning = None
    if recent and recent["cnt"] > 0:
        warning = (
            f"⚠️ You have already shared {recent['cnt']} article(s) with this doctor "
            f"in the last 30 days. Recommended frequency is 1–2/month."
        )

    # Log the share
    log_id = str(uuid.uuid4())
    conn.execute(
        """INSERT INTO share_logs (id, content_id, doctor_id, doctor_name, channel, shared_at, shared_by)
           VALUES (?,?,?,?,?,?,?)""",
        (log_id, content_id, req.doctor_id, req.doctor_name,
         req.channel, now_iso(), req.shared_by)
    )
    conn.commit()
    conn.close()

    return {
        "message": f"Content shared via {req.channel} with {req.doctor_name}.",
        "log_id": log_id,
        "warning": warning,
    }


@app.get("/share-logs")
def get_share_logs():
    """Return sharing history."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM share_logs ORDER BY shared_at DESC").fetchall()
    conn.close()
    return {"logs": [dict(r) for r in rows]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
