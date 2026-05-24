"""
PinnacleIQ — Azure Databricks / Delta Lake Store
=================================================

Handles all reads and writes to Delta Lake tables in Databricks.

WHY DATABRICKS (not SQL Server / Postgres)?
  - Mankind already has an Azure Databricks workspace → zero new infra
  - Delta Lake natively stores ARRAY<STRING> — no JSON string hacks
  - Unity Catalog enforces multi-BU data isolation (row-level security)
  - Delta Lake time travel = full audit trail of every content change
  - Analytics team can join doctor engagement + content tables in same platform

TABLES (Unity Catalog path: <catalog>.<schema>.<table>)
  content_items   — every AI-generated content card (pending/approved/rejected)
  share_logs      — every time a BU Head shares content with a doctor

CONNECTION SETUP (Azure Databricks console):
  1. Go to your Databricks workspace → SQL Warehouses → pick or create one
  2. Click the warehouse → "Connection details" tab
  3. Copy:  Server hostname   → DATABRICKS_HOST
            HTTP path         → DATABRICKS_HTTP_PATH
  4. Go to Settings → Developer → Access tokens → Generate new token
     Copy the token           → DATABRICKS_TOKEN
  5. (Optional) Create a Unity Catalog:
     Run in a Databricks notebook:
       CREATE CATALOG IF NOT EXISTS pinnacleiq;
       CREATE SCHEMA IF NOT EXISTS pinnacleiq.medical_content;

ENV VARS REQUIRED:
  DATABRICKS_HOST        e.g. adb-1234567890123.1.azuredatabricks.net
  DATABRICKS_HTTP_PATH   e.g. /sql/1.0/warehouses/abc1234def567890
  DATABRICKS_TOKEN       personal access token or service principal token
  DATABRICKS_CATALOG     default: pinnacleiq
  DATABRICKS_SCHEMA      default: medical_content
"""

import os
import uuid
from datetime import datetime, timezone
from typing import Optional

# databricks-sql-connector: the official Python driver for Databricks SQL
# Install: pip install databricks-sql-connector
from databricks import sql


# ─────────────────────────────────────────────────────────────────────────────
# Connection helper
# ─────────────────────────────────────────────────────────────────────────────

def _get_connection():
    """
    Open a Databricks SQL connection using env var credentials.

    Returns a databricks.sql.client.Connection object.
    Always use as a context manager:
        with _get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(...)
    """
    return sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )


# ─────────────────────────────────────────────────────────────────────────────
# DatabricksStore class
# ─────────────────────────────────────────────────────────────────────────────

class DatabricksStore:
    """
    Manages all PinnacleIQ data in Azure Databricks Delta Lake.

    Usage:
        store = DatabricksStore()
        store.setup()                  # creates tables if they don't exist
        store.save_content_card(card)  # save a new content card
        items = store.list_content()   # list all content
        store.approve("card-id")       # MA approves a card
        store.share("card-id", ...)    # BU Head shares with a doctor
    """

    def __init__(self):
        # Full table paths using Unity Catalog: catalog.schema.table
        catalog = os.getenv("DATABRICKS_CATALOG", "pinnacleiq")
        schema  = os.getenv("DATABRICKS_SCHEMA", "medical_content")
        self.content_table   = f"`{catalog}`.`{schema}`.`content_items`"
        self.share_log_table = f"`{catalog}`.`{schema}`.`share_logs`"

    # ── Setup ─────────────────────────────────────────────────────────────────

    def setup(self) -> None:
        """
        Create the Delta Lake tables if they don't already exist.
        Safe to call multiple times (idempotent — uses IF NOT EXISTS).

        Run this once when you first deploy, or on every app start.

        Delta Lake table advantages over SQLite:
          - ARRAY<STRING> columns → no JSON string hacks for lists
          - PARTITIONED BY specialty → fast queries per medical specialty / BU
          - Time travel built in → full audit trail for compliance
          - ACID transactions → safe concurrent writes from multiple pipelines
        """
        with _get_connection() as conn:
            with conn.cursor() as cursor:

                # ── content_items table ───────────────────────────────────────
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.content_table} (
                        id               STRING        NOT NULL,
                        topic            STRING        NOT NULL,
                        title            STRING,
                        specialty        STRING,
                        therapy_area     STRING,
                        sub_category     STRING,

                        -- ARRAY<STRING> is native in Delta Lake.
                        -- No JSON string encoding needed (unlike SQLite).
                        tags             ARRAY<STRING>,
                        key_findings     ARRAY<STRING>,
                        recommendations  ARRAY<STRING>,
                        emerging_trends  ARRAY<STRING>,

                        summary          STRING,
                        clinical_insights STRING,
                        short_article    STRING,
                        evidence_quality STRING,

                        -- Workflow status: pending_review → approved / rejected
                        status           STRING        DEFAULT 'pending_review',
                        rejection_reason STRING,

                        created_at       TIMESTAMP,
                        reviewed_at      TIMESTAMP,
                        source           STRING        DEFAULT 'ai_agent',
                        llm_provider     STRING,
                        pipeline         STRING
                    )
                    USING DELTA
                    PARTITIONED BY (specialty)
                    COMMENT 'PinnacleIQ AI-generated medical content cards'
                """)

                # ── share_logs table ──────────────────────────────────────────
                # Records every time content is shared with a doctor.
                # Used for 30-day frequency checks and analytics.
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {self.share_log_table} (
                        id           STRING    NOT NULL,
                        content_id   STRING    NOT NULL,
                        doctor_id    STRING,
                        doctor_name  STRING,
                        specialty    STRING,     -- doctor's specialty
                        channel      STRING,     -- 'whatsapp', 'email'
                        shared_at    TIMESTAMP,
                        shared_by    STRING      -- BU Head name
                    )
                    USING DELTA
                    COMMENT 'PinnacleIQ content sharing history'
                """)

        print("[DatabricksStore] Tables ready ✓")

    # ── Write: save a new content card ────────────────────────────────────────

    def save_content_card(self, card: dict) -> str:
        """
        Save a PinnacleContentCard (from Agent Delta) as a new row in Delta Lake.

        Args:
            card: The dict returned by run_delta() — must contain all portal fields.

        Returns:
            The content ID (UUID string).

        Note on ARRAY columns:
            Databricks SQL connector accepts Python lists directly for ARRAY columns.
            No json.dumps() needed — that was a SQLite workaround.
        """
        content_id = card.get("id") or str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        with _get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {self.content_table}
                    (id, topic, title, specialty, therapy_area, sub_category,
                     tags, key_findings, recommendations, emerging_trends,
                     summary, clinical_insights, short_article, evidence_quality,
                     status, created_at, source, llm_provider, pipeline)
                    VALUES
                    (?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?,
                     ?, ?, ?, ?,
                     'pending_review', ?, 'ai_agent', ?, ?)
                    """,
                    (
                        content_id,
                        card.get("topic", ""),
                        card.get("title", ""),
                        card.get("specialty", "General Medicine"),
                        card.get("therapy_area", "General"),
                        card.get("sub_category", "Review Article"),

                        # ARRAY<STRING> — pass Python lists directly (no JSON encoding)
                        card.get("tags", []),
                        card.get("key_findings", []),
                        card.get("recommendations", []),
                        card.get("emerging_trends", []),

                        card.get("summary", ""),
                        card.get("clinical_insights", ""),
                        card.get("short_article", ""),
                        card.get("evidence_quality", ""),

                        now,
                        card.get("llm_provider", "openrouter"),
                        card.get("pipeline", "Alpha→Beta→Gamma→Delta"),
                    )
                )

        print(f"[DatabricksStore] Content card saved → {content_id}")
        return content_id

    # ── Read: list content ────────────────────────────────────────────────────

    def list_content(
        self,
        status: Optional[str] = None,
        specialty: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        List content cards with optional filters.

        Args:
            status:    Filter by 'pending_review', 'approved', 'rejected'. None = all.
            specialty: Filter by medical specialty (e.g. 'Diabetology').
                       Databricks uses partition pruning here → very fast.
            limit:     Max rows to return (default 100).

        Returns:
            List of content card dicts.
        """
        # Build WHERE clause dynamically
        conditions = []
        params = []

        if status:
            conditions.append("status = ?")
            params.append(status)
        if specialty:
            # Specialty is a partition column → extremely fast filter
            conditions.append("specialty = ?")
            params.append(specialty)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        with _get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT * FROM {self.content_table}
                    {where}
                    ORDER BY created_at DESC
                    LIMIT {limit}
                    """,
                    params or None,
                )
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]

        return [dict(zip(columns, row)) for row in rows]

    def get_content(self, content_id: str) -> Optional[dict]:
        """Get a single content card by ID."""
        with _get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM {self.content_table} WHERE id = ?",
                    (content_id,)
                )
                row = cursor.fetchone()
                if not row:
                    return None
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))

    # ── Workflow: approve / reject ────────────────────────────────────────────

    def approve(self, content_id: str, reviewer: str = "MA Reviewer") -> None:
        """
        Medical Affairs approves a content card.
        Status changes: pending_review → approved.

        Delta Lake records this change with a new transaction version —
        the old 'pending_review' state is preserved in the time travel history.
        """
        now = datetime.now(timezone.utc)
        with _get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {self.content_table}
                    SET status = 'approved', reviewed_at = ?
                    WHERE id = ? AND status = 'pending_review'
                    """,
                    (now, content_id)
                )
        print(f"[DatabricksStore] Content {content_id} approved by {reviewer}")

    def reject(self, content_id: str, reason: str, reviewer: str = "MA Reviewer") -> None:
        """Medical Affairs rejects a content card with a reason."""
        now = datetime.now(timezone.utc)
        with _get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {self.content_table}
                    SET status = 'rejected', rejection_reason = ?, reviewed_at = ?
                    WHERE id = ?
                    """,
                    (reason, now, content_id)
                )
        print(f"[DatabricksStore] Content {content_id} rejected: {reason}")

    # ── Workflow: share with doctor ───────────────────────────────────────────

    def log_share(
        self,
        content_id: str,
        doctor_id: str,
        doctor_name: str,
        doctor_specialty: str,
        channel: str,
        shared_by: str,
    ) -> dict:
        """
        Log a content share event and check 30-day frequency.

        Args:
            content_id:       ID of the approved content card.
            doctor_id:        Doctor's ID from Superman CRM.
            doctor_name:      Doctor's name for display.
            doctor_specialty: Doctor's specialty (for analytics).
            channel:          'whatsapp' or 'email'.
            shared_by:        BU Head's name.

        Returns:
            dict with log_id and optional frequency warning.
        """
        log_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        with _get_connection() as conn:
            with conn.cursor() as cursor:

                # ── 30-day frequency check ────────────────────────────────────
                # How many times has this doctor received content in last 30 days?
                # This uses Databricks SQL date functions.
                cursor.execute(
                    f"""
                    SELECT COUNT(*) as cnt
                    FROM {self.share_log_table}
                    WHERE doctor_id = ?
                      AND shared_at >= DATEADD(DAY, -30, CURRENT_TIMESTAMP())
                    """,
                    (doctor_id,)
                )
                row = cursor.fetchone()
                shares_last_30_days = row[0] if row else 0

                warning = None
                if shares_last_30_days >= 2:
                    warning = (
                        f"⚠️ {doctor_name} has already received {shares_last_30_days} "
                        f"article(s) in the last 30 days. Recommended: 1–2/month."
                    )

                # ── Write the share log ───────────────────────────────────────
                cursor.execute(
                    f"""
                    INSERT INTO {self.share_log_table}
                    (id, content_id, doctor_id, doctor_name, specialty, channel, shared_at, shared_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (log_id, content_id, doctor_id, doctor_name,
                     doctor_specialty, channel, now, shared_by)
                )

        return {"log_id": log_id, "warning": warning}

    # ── Analytics queries (Databricks advantage over SQLite) ─────────────────

    def get_sharing_analytics(self, specialty: Optional[str] = None) -> dict:
        """
        Aggregate sharing analytics — only possible because we're on Databricks.

        Returns content performance metrics:
          - Total shares per therapy area
          - Most shared content cards
          - Doctor engagement by specialty
          - Shares per channel (WhatsApp vs email)
        """
        specialty_filter = f"WHERE s.specialty = '{specialty}'" if specialty else ""

        with _get_connection() as conn:
            with conn.cursor() as cursor:

                # Shares by therapy area
                cursor.execute(f"""
                    SELECT c.therapy_area, COUNT(*) as total_shares
                    FROM {self.share_log_table} s
                    JOIN {self.content_table} c ON s.content_id = c.id
                    {specialty_filter}
                    GROUP BY c.therapy_area
                    ORDER BY total_shares DESC
                """)
                by_therapy = [{"therapy_area": r[0], "shares": r[1]}
                              for r in cursor.fetchall()]

                # Shares by channel
                cursor.execute(f"""
                    SELECT channel, COUNT(*) as cnt
                    FROM {self.share_log_table} s
                    JOIN {self.content_table} c ON s.content_id = c.id
                    {specialty_filter}
                    GROUP BY channel
                """)
                by_channel = [{"channel": r[0], "count": r[1]}
                              for r in cursor.fetchall()]

                # Content approval rate
                cursor.execute(f"""
                    SELECT status, COUNT(*) as cnt
                    FROM {self.content_table}
                    {f"WHERE specialty = '{specialty}'" if specialty else ""}
                    GROUP BY status
                """)
                by_status = {r[0]: r[1] for r in cursor.fetchall()}

        return {
            "shares_by_therapy_area": by_therapy,
            "shares_by_channel":      by_channel,
            "content_by_status":      by_status,
        }

    def get_share_logs(self, content_id: Optional[str] = None) -> list[dict]:
        """Return sharing history, optionally filtered by content_id."""
        where = f"WHERE content_id = '{content_id}'" if content_id else ""
        with _get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT * FROM {self.share_log_table} {where} ORDER BY shared_at DESC"
                )
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
