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
            status:    'pending_review' | 'approved' | 'rejected' |
                       'improvement_requested' | None (all)
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

    @abstractmethod
    def request_improvement(
        self,
        content_id: str,
        notes: str,
        reviewer: str = "MA Reviewer",
    ) -> None:
        """
        Medical Affairs requests improvement on a content card.
        Sets status='improvement_requested' and saves improvement_notes.

        Args:
            content_id: ID of the content card to improve.
            notes:      Free-text feedback from MA (e.g. "Fix empagliflozin dose").
            reviewer:   Name of the MA reviewer requesting improvement.
        """
        ...

    @abstractmethod
    def save_improved_content(self, card: dict, parent_id: str, version: int) -> str:
        """
        Save a new revised version of a content card, linking it back to the
        original (or root) card via parent_id.

        Args:
            card:      Content dict for the improved version.
            parent_id: ID of the original (root) content card.
            version:   Version number (2, 3, ...).

        Returns:
            The content ID of the newly saved improved card.
        """
        ...

    @abstractmethod
    def get_content_versions(self, root_id: str) -> list[dict]:
        """
        Return all versions of a content card — the original plus all
        improvement revisions — ordered by version ascending.

        Args:
            root_id: The ID of the original (v1) content card.

        Returns:
            List of content card dicts with version/parent_id populated.
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

    # ── Notifications ─────────────────────────────────────────────────────────

    @abstractmethod
    def add_notification(
        self,
        type: str,
        content_id: str,
        title: str,
        message: str,
        division: str,
    ) -> str:
        """
        Create a new in-app notification.

        Args:
            type:       Notification type e.g. 'new_content', 'content_approved',
                        'improvement_ready'.
            content_id: Related content card ID.
            title:      Short notification title.
            message:    Full notification message body.
            division:   Division this notification is relevant to.

        Returns:
            The notification ID (UUID string).
        """
        ...

    @abstractmethod
    def get_notifications(
        self,
        division: Optional[str] = None,
        unread_only: bool = False,
    ) -> list[dict]:
        """
        Retrieve notifications, optionally filtered.

        Args:
            division:    Filter by division. None = all divisions.
            unread_only: If True, only return notifications where read_at IS NULL.

        Returns:
            List of notification dicts, newest first.
        """
        ...

    @abstractmethod
    def mark_notification_read(self, notification_id: str) -> None:
        """
        Mark a notification as read by setting read_at to now.

        Args:
            notification_id: The notification UUID to mark as read.
        """
        ...
