from .base import BaseStore
from .factory import get_store
from .sqlite_store import SQLiteStore

try:
    from .databricks_store import DatabricksStore
    __all__ = ["BaseStore", "get_store", "SQLiteStore", "DatabricksStore"]
except ImportError:
    # Databricks module not installed — OK for SQLite demo
    DatabricksStore = None
    __all__ = ["BaseStore", "get_store", "SQLiteStore"]
