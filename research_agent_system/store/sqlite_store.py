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
from typing import Optional

from .base import BaseStore


class SQLiteStore(BaseStore):
    """SQLite-backed store. Used for demos and local development."""

    def __init__(self):
        self.db_path = os.getenv("SQLITE_DB_PATH", "pinnacleiq_demo.db")

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
        """)
        conn.commit()
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
                evidence_quality, status, created_at, source, llm_provider, pipeline)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,'pending_review',?,?,?,?)""",
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
            ),
        )
        conn.commit()
        conn.close()
        print(f"[SQLiteStore] Content card saved → {content_id}")
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
            "UPDATE content_items SET status='rejected', rejection_reason=?, reviewed_at=? WHERE id=?",
            (reason, self._now(), content_id)
        )
        conn.commit()
        conn.close()

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
