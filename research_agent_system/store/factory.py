"""
Store Factory
=============

The single place that decides which storage backend to use.
Every part of the codebase calls get_store() — never importing
SQLiteStore or DatabricksStore directly.

USAGE:
    from store import get_store

    store = get_store()          # reads STORE_BACKEND from .env
    store.setup()
    store.save_content_card(card)

SWITCHING BACKENDS:
    In .env:
      STORE_BACKEND=sqlite       ← demo / local dev (default)
      STORE_BACKEND=databricks   ← production on Mankind's Azure Databricks

    That's it. One line change. Zero code changes anywhere else.
"""

import os
from .base import BaseStore


def get_store() -> BaseStore:
    """
    Return the configured storage backend.

    Reads STORE_BACKEND env var:
      'sqlite'      → SQLiteStore  (default — works with zero setup)
      'databricks'  → DatabricksStore

    Raises:
        ValueError: If STORE_BACKEND is set to an unknown value.
    """
    backend = os.getenv("STORE_BACKEND", "sqlite").lower().strip()

    if backend == "sqlite":
        from .sqlite_store import SQLiteStore
        return SQLiteStore()

    if backend == "databricks":
        from .databricks_store import DatabricksStore
        return DatabricksStore()

    raise ValueError(
        f"Unknown STORE_BACKEND='{backend}'. "
        f"Valid options: 'sqlite' (demo/dev) | 'databricks' (production)"
    )
