"""
PinnacleIQ Daily Job Scheduler
================================
Runs two jobs every morning:

  06:30 AM — Doctor Sync
              Full refresh from Databricks (or JSON cache in demo mode)
              Updates the doctor directory for all divisions.

  07:00 AM — Content Generation
              Generates 1-2 research articles per division based on
              doctor interests. Articles saved as 'pending_review'.
              MA team is notified.

Uses APScheduler (pip install apscheduler).
In production: replace with Azure Databricks Jobs or Azure Functions.
"""
import importlib.util
import os
import threading
import uuid
from datetime import datetime, timezone

_scheduler = None
_job_history: list = []  # last 20 job runs — visible in portal

DIVISIONS = [
    "Gravitas", "Life", "Future", "Discovery", "Oncology",
    "Nephrology", "Neuro", "Derma", "Ortho", "Ophthalmology",
]

DIVISION_TOPICS = {
    "Gravitas":  [("SGLT2 Inhibitors and Cardiovascular Outcomes",     "Cardiology",    "SGLT2"),
                  ("GLP-1 Receptor Agonists in Type 2 Diabetes",       "Diabetology",   "GLP-1")],
    "Life":      [("PCOS Management: Inositol vs Metformin",           "Gynaecology",   "PCOS"),
                  ("Iron Deficiency Anaemia in Paediatrics",            "Paediatrics",   "Haematology")],
    "Future":    [("Empagliflozin in Heart Failure — ESC 2025 Update", "Cardiology",    "SGLT2"),
                  ("Thyroid Disorders: Updated Management Guidelines",  "Endocrinology", "Thyroid")],
    "Discovery": [("Retinoids in Acne: New Formulation Evidence",      "Dermatology",   "Acne"),
                  ("Migraine Prophylaxis: CGRP Antagonists 2025",      "Neurology",     "Migraine")],
}
DEFAULT_TOPICS = [
    ("Evidence-Based Hypertension Management 2025",   "Cardiology",  "Hypertension"),
    ("Metformin: New Roles Beyond Glycaemic Control", "Diabetology", "T2DM"),
]


def _log(job_name: str, status: str, detail: str = ""):
    entry = {
        "job":       job_name,
        "status":    status,
        "detail":    detail,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    _job_history.insert(0, entry)
    if len(_job_history) > 20:
        _job_history.pop()
    print(f"[Scheduler] [{job_name}] {status}: {detail}")


def job_doctor_sync():
    """06:30 AM — Full refresh of doctor data from Databricks."""
    try:
        _log("doctor_sync", "started")
        from doctor_sync import sync_doctors
        result = sync_doctors()
        _log("doctor_sync", "completed",
             f"Synced {result['count']} doctors from {result['source']} in {result['duration_sec']}s")
    except Exception as e:
        _log("doctor_sync", "error", str(e))


def job_content_generation():
    """07:00 AM — Generate 1-2 articles per division and notify MA team."""
    from store import get_store
    from notifications import notify_ma_new_content
    from mock_runner import run_mock_pipeline

    store = get_store()
    articles_generated = 0

    # Rotate through divisions — generate for 2-3 divisions per day to avoid flooding
    today = datetime.now().weekday()  # 0=Mon ... 6=Sun
    start_idx = (today * 3) % len(DIVISIONS)
    day_divisions = DIVISIONS[start_idx:start_idx + 3]
    # Handle wrap-around
    if len(day_divisions) < 3:
        day_divisions += DIVISIONS[:3 - len(day_divisions)]

    for division in day_divisions:
        topics = DIVISION_TOPICS.get(division, DEFAULT_TOPICS)
        # Pick 1 topic per division per day
        topic_tuple = topics[today % len(topics)]
        topic, specialty, therapy_area = topic_tuple

        run_id = str(uuid.uuid4())
        run_store = {
            run_id: {
                "status":        "running",
                "topic":         topic,
                "progress":      0,
                "current_agent": "alpha",
                "status_msg":    "Starting scheduled pipeline...",
                "content_id":    None,
                "division":      division,
            }
        }

        try:
            _log("content_generation", "started", f"{division} — {topic}")
            run_mock_pipeline(
                topic=topic,
                specialty=specialty,
                therapy_area=therapy_area,
                run_store=run_store,
                run_id=run_id,
            )
            run = run_store[run_id]
            if run.get("status") == "completed" and run.get("content"):
                card = {**run["content"], "division": division}
                content_id = store.save_content_card(card)
                run_store[run_id]["content_id"] = content_id
                notify_ma_new_content(store, content_id, card.get("title", topic), specialty, division)
                articles_generated += 1
                _log("content_generation", "completed",
                     f"{division} — '{card.get('title', topic)[:60]}' saved as {content_id}")
        except Exception as e:
            _log("content_generation", "error", f"{division}: {e}")

    _log("content_generation", "summary", f"{articles_generated} articles generated")


def get_job_history() -> list:
    return _job_history


def get_scheduler_status() -> dict:
    if _scheduler is None:
        return {"running": False, "jobs": []}
    jobs = []
    for job in _scheduler.get_jobs():
        next_run = job.next_run_time
        jobs.append({
            "id":       job.id,
            "name":     job.name,
            "next_run": next_run.isoformat() if next_run else None,
        })
    return {"running": _scheduler.running, "jobs": jobs}


def run_job_now(job_name: str) -> dict:
    """Manually trigger a scheduled job immediately (for testing/admin)."""
    if job_name == "doctor_sync":
        t = threading.Thread(target=job_doctor_sync, daemon=True)
        t.start()
        return {"triggered": "doctor_sync"}
    if job_name == "content_generation":
        t = threading.Thread(target=job_content_generation, daemon=True)
        t.start()
        return {"triggered": "content_generation"}
    return {"error": f"Unknown job: {job_name}"}


def start_scheduler(sync_hour: int = 6, sync_minute: int = 30,
                    content_hour: int = 7, content_minute: int = 0) -> None:
    global _scheduler

    # Guard: only start if APScheduler is installed
    if importlib.util.find_spec("apscheduler") is None:
        print("[Scheduler] WARNING: apscheduler not installed — scheduler disabled.")
        print("[Scheduler] Install with: pip install apscheduler>=3.10.4")
        return

    if _scheduler and _scheduler.running:
        print("[Scheduler] Already running")
        return

    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger

    _scheduler = BackgroundScheduler(timezone="Asia/Kolkata")  # IST

    _scheduler.add_job(
        job_doctor_sync,
        CronTrigger(hour=sync_hour, minute=sync_minute),
        id="doctor_sync",
        name=f"Doctor Sync ({sync_hour:02d}:{sync_minute:02d} IST daily)",
        replace_existing=True,
    )
    _scheduler.add_job(
        job_content_generation,
        CronTrigger(hour=content_hour, minute=content_minute),
        id="content_generation",
        name=f"Content Generation ({content_hour:02d}:{content_minute:02d} IST daily)",
        replace_existing=True,
    )

    _scheduler.start()
    print(f"[Scheduler] Started — Doctor sync at {sync_hour:02d}:{sync_minute:02d} IST, "
          f"Content generation at {content_hour:02d}:{content_minute:02d} IST")
    _log("scheduler", "started", "Daily jobs registered")


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        _log("scheduler", "stopped")
        print("[Scheduler] Stopped")
