"""
Abstract Store Interface
========================

Defines the contract that ALL storage backends must implement.
Both SQLiteStore and DatabricksStore implement this exact interface.

WHY THIS MATTERS:
  The rest of the codebase (Delta agent, FastAPI API, portal backend)
  only ever calls methods defined here. They never import SQLite or
  Databricks directly. This means:

  - Demo today     → STORE_BACKEND=sqlite   (zero setup, works instantly)
  - Production     → STORE_BACKEND=databricks (one env var change, nothing else)
  - Future (Azure SQL, Postgres, etc.) → add a new class, zero other changes

PATTERN: Strategy Pattern (also called Dependency Injection)
  The factory (factory.py) decides WHICH implementation to use.
  The callers never know or care which backend is running.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseStore(ABC):
    """
    Abstract base class for PinnacleIQ data storage.
    All methods here must be implemented by every concrete store.
    """

    # ── Setup ─────────────────────────────────────────────────────────────────

    @abstractmethod
    def setup(self) -> None:
        """
        Initialise the storage backend — create tables/schemas if needed.
        Must be safe to call multiple times (idempotent).
        Called once on application startup.
        """
        ...

    # ── Content Cards ─────────────────────────────────────────────────────────

    @abstractmethod
    def save_content_card(self, card: dict) -> str:
        """
        Save a new PinnacleContentCard produced by Agent Delta.

        Args:
            card: dict matching PinnacleContentCard schema.

        Returns:
            The content ID (string UUID) of the saved record.
        """
        ...

    @abstractmethod
    def list_content(
        self,
        status: Optional[str] = None,
        specialty: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        """
        List content cards with optional filters.

        Args:
            status:    'pending_review' | 'approved' | 'rejected' | None (all)
            specialty: Filter by medical specialty. None = all specialties.
            limit:     Max number of rows to return.

        Returns:
            List of content card dicts, newest first.
        """
        ...

    @abstractmethod
    def get_content(self, content_id: str) -> Optional[dict]:
        """
        Fetch a single content card by ID.

        Returns:
            Content card dict, or None if not found.
        """
        ...

    # ── MA Workflow ───────────────────────────────────────────────────────────

    @abstractmethod
    def approve(self, content_id: str, reviewer: str = "MA Reviewer") -> None:
        """
        Medical Affairs approves a content card.
        Status: pending_review → approved.
        """
        ...

    @abstractmethod
    def reject(self, content_id: str, reason: str, reviewer: str = "MA Reviewer") -> None:
        """
        Medical Affairs rejects a content card with a reason.
        Status: pending_review → rejected.
        """
        ...

    # ── Sharing ───────────────────────────────────────────────────────────────

    @abstractmethod
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
        Log a content share event and return frequency warning if applicable.

        Returns:
            dict: { "log_id": str, "warning": str | None }
            warning is non-None if doctor received >2 articles in last 30 days.
        """
        ...

    @abstractmethod
    def get_share_logs(self, content_id: Optional[str] = None) -> list[dict]:
        """
        Return sharing history, optionally filtered by content_id.
        """
        ...
