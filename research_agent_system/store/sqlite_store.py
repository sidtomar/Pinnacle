"""
SQLite Store — Demo & Local Development
=======================================

Implements BaseStore using SQLite — a single file database
that requires zero installation or configuration.

WHEN TO USE:
  - Management demos          (STORE_BACKEND=sqlite)
  - Local development/testing (STORE_BACKEND=sqlite)
  - Running without internet   (STORE_BACKEND=sqlite)

WHEN NOT TO USE:
  - Production (use DatabricksStore)
  - Multi-user concurrent access (SQLite has write locks)
  - Analytics queries across BUs (SQLite has no Spark/SQL analytics)

DB FILE LOCATION:
  Defaults to ./pinnacleiq_demo.db in the current directory.
  Override with SQLITE_DB_PATH env var.

MIGRATION PATH:
  When management approves and you go to production:
    1. Change STORE_BACKEND=databricks in .env
    2. Done. Nothing else changes.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .base import BaseStore

# Always resolve to demo/backend/pinnacleiq_demo.db regardless of launch CWD.
# sqlite_store.py lives at research_agent_system/store/ — three parents up is
# the project root, then down to demo/backend/.
_DEFAULT_DB = str(Path(__file__).resolve().parent.parent.parent / "demo" / "backend" / "pinnacleiq_demo.db")


class SQLiteStore(BaseStore):
    """SQLite-backed store. Used for demos and local development."""

    def __init__(self):
        self.db_path = os.getenv("SQLITE_DB_PATH", _DEFAULT_DB)

    def _conn(self) -> sqlite3.Connection:
        """Open a connection with dict-style row access."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ── Setup ─────────────────────────────────────────────────────────────────

    def setup(self) -> None:
        """Create tables if they don't exist. Safe to call multiple times."""
        conn = self._conn()
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS content_items (
                id                TEXT PRIMARY KEY,
                topic             TEXT NOT NULL,
                title             TEXT,
                specialty         TEXT,
                therapy_area      TEXT,
                sub_category      TEXT,
                tags              TEXT,          -- stored as JSON string (SQLite limitation)
                summary           TEXT,
                key_findings      TEXT,          -- stored as JSON string
                clinical_insights TEXT,
                recommendations   TEXT,          -- stored as JSON string
                emerging_trends   TEXT,          -- stored as JSON string
                short_article     TEXT,
                evidence_quality  TEXT,
                status            TEXT DEFAULT 'pending_review',
                rejection_reason  TEXT,
                created_at        TEXT,
                reviewed_at       TEXT,
                source            TEXT DEFAULT 'ai_agent',
                llm_provider      TEXT,
                pipeline          TEXT
            );

            CREATE TABLE IF NOT EXISTS share_logs (
                id           TEXT PRIMARY KEY,
                content_id   TEXT NOT NULL,
                doctor_id    TEXT,
                doctor_name  TEXT,
                specialty    TEXT,
                channel      TEXT,
                shared_at    TEXT,
                shared_by    TEXT
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id          TEXT PRIMARY KEY,
                type        TEXT NOT NULL,
                content_id  TEXT,
                title       TEXT,
                message     TEXT,
                division    TEXT,
                created_at  TEXT,
                read_at     TEXT
            );
        """)
        conn.commit()

        # ── Schema migrations: add new columns to existing content_items table ──
        # Uses try/except so it's safe to run against an existing DB.
        migrations = [
            "ALTER TABLE content_items ADD COLUMN version INTEGER DEFAULT 1",
            "ALTER TABLE content_items ADD COLUMN parent_id TEXT",
            "ALTER TABLE content_items ADD COLUMN improvement_notes TEXT",
            "ALTER TABLE content_items ADD COLUMN reviewer TEXT",
            "ALTER TABLE content_items ADD COLUMN division TEXT",
            "ALTER TABLE content_items ADD COLUMN source_journals TEXT",
            "ALTER TABLE content_items ADD COLUMN pmid TEXT",
            "ALTER TABLE content_items ADD COLUMN doi TEXT",
            "ALTER TABLE content_items ADD COLUMN authors TEXT",
            "ALTER TABLE content_items ADD COLUMN relevant_doctor_specialties TEXT",
            "ALTER TABLE content_items ADD COLUMN whatsapp_summary TEXT",
            "ALTER TABLE content_items ADD COLUMN pubmed_link TEXT",
            "ALTER TABLE content_items ADD COLUMN full_text_link TEXT",
            "ALTER TABLE content_items ADD COLUMN publication_date TEXT",
        ]
        for sql in migrations:
            try:
                conn.execute(sql)
                conn.commit()
            except Exception:
                pass  # column already exists — safe to ignore

        conn.close()
        print(f"[SQLiteStore] Ready — {self.db_path}")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _serialize(self, value):
        """Convert lists to JSON strings for SQLite storage."""
        if isinstance(value, list):
            return json.dumps(value)
        return value

    def _deserialize(self, row: sqlite3.Row) -> dict:
        """Convert a Row to dict, parsing JSON array fields back to lists."""
        d = dict(row)
        for field in ("tags", "key_findings", "recommendations", "emerging_trends"):
            if d.get(field) and isinstance(d[field], str):
                try:
                    d[field] = json.loads(d[field])
                except Exception:
                    d[field] = []
        return d

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ── Content Cards ─────────────────────────────────────────────────────────

    def save_content_card(self, card: dict) -> str:
        content_id = card.get("id") or str(uuid.uuid4())


        conn = self._conn()
        conn.execute(
            """INSERT INTO content_items
               (id, topic, title, specialty, therapy_area, sub_category,
                tags, summary, key_findings, clinical_insights,
                recommendations, emerging_trends, short_article,
                evidence_quality, status, created_at, source, llm_provider, pipeline,
                version, parent_id, improvement_notes, reviewer, division, source_journals,
                pmid, doi, authors, relevant_doctor_specialties, whatsapp_summary,
                pubmed_link, full_text_link, publication_date)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending_review',?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                content_id,
                card.get("topic", ""),
                card.get("title", ""),
                card.get("specialty", "General Medicine"),
                card.get("therapy_area", "General"),
                card.get("sub_category", "Review Article"),
                self._serialize(card.get("tags", [])),
                card.get("summary", ""),
                self._serialize(card.get("key_findings", [])),
                card.get("clinical_insights", ""),
                self._serialize(card.get("recommendations", [])),
                self._serialize(card.get("emerging_trends", [])),
                card.get("short_article", ""),
                card.get("evidence_quality", ""),
                self._now(),
                "ai_agent",
                card.get("llm_provider", "openrouter"),
                card.get("pipeline", "Alpha→Beta→Gamma→Delta"),
                card.get("version", 1),
                card.get("parent_id", None),
                card.get("improvement_notes", None),
                card.get("reviewer", None),
                card.get("division", None),
                card.get("source_journals", None),
                card.get("pmid", None),
                card.get("doi", None),
                card.get("authors", None),
                card.get("relevant_doctor_specialties", None),
                card.get("whatsapp_summary", None),
                card.get("pubmed_link", None),
                card.get("full_text_link", None),
                card.get("publication_date", None),
            ),
        )
        conn.commit()
        conn.close()
        print(f"[SQLiteStore] Content card saved: {content_id}")
        return content_id

    def list_content(
        self,
        status: Optional[str] = None,
        specialty: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        conn = self._conn()
        if status and specialty:
            rows = conn.execute(
                "SELECT * FROM content_items WHERE status=? AND specialty=? ORDER BY created_at DESC LIMIT ?",
                (status, specialty, limit)
            ).fetchall()
        elif status:
            rows = conn.execute(
                "SELECT * FROM content_items WHERE status=? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            ).fetchall()
        elif specialty:
            rows = conn.execute(
                "SELECT * FROM content_items WHERE specialty=? ORDER BY created_at DESC LIMIT ?",
                (specialty, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM content_items ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        conn.close()
        return [self._deserialize(r) for r in rows]

    def get_content(self, content_id: str) -> Optional[dict]:
        conn = self._conn()
        row = conn.execute(
            "SELECT * FROM content_items WHERE id=?", (content_id,)
        ).fetchone()
        conn.close()
        return self._deserialize(row) if row else None

    # ── MA Workflow ───────────────────────────────────────────────────────────

    def approve(self, content_id: str, reviewer: str = "MA Reviewer") -> None:
        conn = self._conn()
        conn.execute(
            "UPDATE content_items SET status='approved', reviewed_at=? WHERE id=?",
            (self._now(), content_id)
        )
        conn.commit()
        conn.close()

    def reject(self, content_id: str, reason: str, reviewer: str = "MA Reviewer") -> None:
        conn = self._conn()
        conn.execute(
            "UPDATE content_items SET status='rejected', rejection_reason=?, reviewed_at=?, reviewer=? WHERE id=?",
            (reason, self._now(), reviewer, content_id)
        )
        conn.commit()
        conn.close()

    def request_improvement(
        self,
        content_id: str,
        notes: str,
        reviewer: str = "MA Reviewer",
    ) -> None:
        """Set status to improvement_requested and store MA notes."""
        conn = self._conn()
        conn.execute(
            """UPDATE content_items
               SET status='improvement_requested', improvement_notes=?,
                   reviewer=?, reviewed_at=?
               WHERE id=?""",
            (notes, reviewer, self._now(), content_id)
        )
        conn.commit()
        conn.close()
        print(f"[SQLiteStore] Improvement requested for {content_id} by {reviewer}")

    def save_improved_content(self, card: dict, parent_id: str, version: int) -> str:
        """Save a new version of a content card, linked to parent_id."""
        content_id = card.get("id") or str(uuid.uuid4())
        conn = self._conn()
        conn.execute(
            """INSERT INTO content_items
               (id, topic, title, specialty, therapy_area, sub_category,
                tags, summary, key_findings, clinical_insights,
                recommendations, emerging_trends, short_article,
                evidence_quality, status, created_at, source, llm_provider, pipeline,
                version, parent_id, improvement_notes, reviewer, division, source_journals,
                pmid, doi, authors, relevant_doctor_specialties, whatsapp_summary,
                pubmed_link, full_text_link, publication_date)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending_review',?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                content_id,
                card.get("topic", ""),
                card.get("title", ""),
                card.get("specialty", "General Medicine"),
                card.get("therapy_area", "General"),
                card.get("sub_category", "Review Article"),
                self._serialize(card.get("tags", [])),
                card.get("summary", ""),
                self._serialize(card.get("key_findings", [])),
                card.get("clinical_insights", ""),
                self._serialize(card.get("recommendations", [])),
                self._serialize(card.get("emerging_trends", [])),
                card.get("short_article", ""),
                card.get("evidence_quality", ""),
                self._now(),
                "ai_agent",
                card.get("llm_provider", "openrouter"),
                card.get("pipeline", f"Improvement v{version} · Beta+Gamma re-run"),
                version,
                parent_id,
                card.get("improvement_notes", None),
                card.get("reviewer", None),
                card.get("division", None),
                card.get("source_journals", None),
                card.get("pmid", None),
                card.get("doi", None),
                card.get("authors", None),
                card.get("relevant_doctor_specialties", None),
                card.get("whatsapp_summary", None),
                card.get("pubmed_link", None),
                card.get("full_text_link", None),
                card.get("publication_date", None),
            ),
        )
        conn.commit()
        conn.close()
        print(f"[SQLiteStore] Improved content saved: {content_id} (v{version}, parent={parent_id})")
        return content_id

    def get_content_versions(self, root_id: str) -> list[dict]:
        """Return all versions of a content card (original + all improvements)."""
        conn = self._conn()
        # The original card has id=root_id; improved cards have parent_id=root_id
        rows = conn.execute(
            """SELECT * FROM content_items
               WHERE id=? OR parent_id=?
               ORDER BY version ASC, created_at ASC""",
            (root_id, root_id)
        ).fetchall()
        conn.close()
        return [self._deserialize(r) for r in rows]

    # ── Sharing ───────────────────────────────────────────────────────────────

    def log_share(
        self,
        content_id: str,
        doctor_id: str,
        doctor_name: str,
        doctor_specialty: str,
        channel: str,
        shared_by: str,
    ) -> dict:
        conn = self._conn()

        # 30-day frequency check
        row = conn.execute(
            """SELECT COUNT(*) as cnt FROM share_logs
               WHERE doctor_id=? AND shared_at > datetime('now','-30 days')""",
            (doctor_id,)
        ).fetchone()
        count = row[0] if row else 0

        warning = None
        if count >= 2:
            warning = (
                f"⚠️ {doctor_name} has already received {count} article(s) "
                f"in the last 30 days. Recommended: 1–2/month."
            )

        log_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO share_logs
               (id, content_id, doctor_id, doctor_name, specialty, channel, shared_at, shared_by)
               VALUES (?,?,?,?,?,?,?,?)""",
            (log_id, content_id, doctor_id, doctor_name,
             doctor_specialty, channel, self._now(), shared_by)
        )
        conn.commit()
        conn.close()
        return {"log_id": log_id, "warning": warning}

    def get_share_logs(self, content_id: Optional[str] = None) -> list[dict]:
        conn = self._conn()
        if content_id:
            rows = conn.execute(
                "SELECT * FROM share_logs WHERE content_id=? ORDER BY shared_at DESC",
                (content_id,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM share_logs ORDER BY shared_at DESC"
            ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── Notifications ─────────────────────────────────────────────────────────

    def add_notification(
        self,
        type: str,
        content_id: str,
        title: str,
        message: str,
        division: str,
    ) -> str:
        """Create a new in-app notification. Returns the notification ID."""
        notification_id = str(uuid.uuid4())
        conn = self._conn()
        conn.execute(
            """INSERT INTO notifications
               (id, type, content_id, title, message, division, created_at, read_at)
               VALUES (?,?,?,?,?,?,?,NULL)""",
            (notification_id, type, content_id, title, message, division, self._now())
        )
        conn.commit()
        conn.close()
        print(f"[SQLiteStore] Notification created: {notification_id} ({type})")
        return notification_id

    def get_notifications(
        self,
        division: Optional[str] = None,
        unread_only: bool = False,
    ) -> list[dict]:
        """Retrieve notifications, optionally filtered by division or unread status."""
        conn = self._conn()
        conditions = []
        params = []

        if division:
            conditions.append("division=?")
            params.append(division)
        if unread_only:
            conditions.append("read_at IS NULL")

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = conn.execute(
            f"SELECT * FROM notifications {where} ORDER BY created_at DESC",
            params
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def mark_notification_read(self, notification_id: str) -> None:
        """Mark a notification as read by setting read_at to now."""
        conn = self._conn()
        conn.execute(
            "UPDATE notifications SET read_at=? WHERE id=?",
            (self._now(), notification_id)
        )
        conn.commit()
        conn.close()
