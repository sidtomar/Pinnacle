"""
Doctor Sync Service — pulls Pinnacle doctor records from Databricks.

Architecture:
  Superman CRM -> Databricks Delta table (daily push, they control this)
  Pinnacle Sync (this module) -> reads from that table -> local cache

Since there are only ~50 doctors per division (~1,150 total), a full refresh
every morning is correct — no need for delta detection.

CONFIGURATION (env vars — fill in once Databricks team shares schema):
  SUPERMAN_DOCTOR_TABLE    Full Unity Catalog path  e.g. superman_crm.doctors.hcp_master
  SUPERMAN_COL_ID          Doctor unique ID column   e.g. hcp_id
  SUPERMAN_COL_NAME        Full name column          e.g. full_name
  SUPERMAN_COL_PHONE       WhatsApp phone column     e.g. mobile
  SUPERMAN_COL_EMAIL       Email column              e.g. email
  SUPERMAN_COL_SPECIALTY   Specialty column          e.g. specialty
  SUPERMAN_COL_DIVISION    Division column           e.g. division
  SUPERMAN_COL_TIER        Tier column               e.g. tier (A/B/C)
  SUPERMAN_COL_HOSPITAL    Hospital/clinic column    e.g. hospital_name
  SUPERMAN_COL_CITY        City column               e.g. city
  SUPERMAN_COL_INTERESTS   Interests column          e.g. therapy_interests (may be CSV string)
"""
import json, os, time
from datetime import datetime, timezone
from pathlib import Path

# -- Column name mapping from env ---------------------------------------------
def _col(env_key: str, default: str) -> str:
    return os.getenv(env_key, default)

DOCTOR_TABLE  = lambda: os.getenv("SUPERMAN_DOCTOR_TABLE", "")
COL_ID        = lambda: _col("SUPERMAN_COL_ID",        "doctor_id")
COL_NAME      = lambda: _col("SUPERMAN_COL_NAME",      "full_name")
COL_PHONE     = lambda: _col("SUPERMAN_COL_PHONE",     "mobile")
COL_EMAIL     = lambda: _col("SUPERMAN_COL_EMAIL",     "email")
COL_SPECIALTY = lambda: _col("SUPERMAN_COL_SPECIALTY", "specialty")
COL_DIVISION  = lambda: _col("SUPERMAN_COL_DIVISION",  "division")
COL_TIER      = lambda: _col("SUPERMAN_COL_TIER",      "tier")
COL_HOSPITAL  = lambda: _col("SUPERMAN_COL_HOSPITAL",  "hospital")
COL_CITY      = lambda: _col("SUPERMAN_COL_CITY",      "city")
COL_INTERESTS = lambda: _col("SUPERMAN_COL_INTERESTS", "therapy_interests")
COL_SUB_SPEC  = lambda: _col("SUPERMAN_COL_SUB_SPEC",  "sub_specialty")
COL_LAST_MOD  = lambda: _col("SUPERMAN_COL_LAST_MOD",  "updated_at")

# Cache file path — sits next to doctors.json in demo/
CACHE_PATH = Path(os.getenv("DOCTOR_CACHE_PATH",
                  str(Path(__file__).parent.parent / "doctors.json")))

_sync_state = {
    "last_sync_at":     None,
    "last_sync_count":  0,
    "last_sync_status": "never",
    "last_sync_error":  None,
}


def get_sync_status() -> dict:
    return {**_sync_state}


def sync_doctors(division_filter: str = None) -> dict:
    """
    Main sync entry point. Tries Databricks first; falls back to local JSON.

    Args:
        division_filter: If set, only sync doctors for this division.
                         None = sync all divisions.
    Returns:
        { "count": int, "source": "databricks"|"json_cache", "duration_sec": float }
    """
    t0 = time.time()
    table = DOCTOR_TABLE()

    if table:
        try:
            result = _sync_from_databricks(division_filter)
            _sync_state.update({
                "last_sync_at":     datetime.now(timezone.utc).isoformat(),
                "last_sync_count":  result["count"],
                "last_sync_status": "ok",
                "last_sync_error":  None,
            })
            result["duration_sec"] = round(time.time() - t0, 2)
            print(f"[DoctorSync] Synced {result['count']} doctors from Databricks in {result['duration_sec']}s")
            return result
        except Exception as e:
            _sync_state["last_sync_error"]  = str(e)
            _sync_state["last_sync_status"] = "error"
            print(f"[DoctorSync] Databricks sync failed: {e} — falling back to JSON cache")

    result = _sync_from_json(division_filter)
    _sync_state.update({
        "last_sync_at":     datetime.now(timezone.utc).isoformat(),
        "last_sync_count":  result["count"],
        "last_sync_status": "json_fallback",
    })
    result["duration_sec"] = round(time.time() - t0, 2)
    print(f"[DoctorSync] Loaded {result['count']} doctors from JSON cache in {result['duration_sec']}s")
    return result


def _sync_from_databricks(division_filter: str = None) -> dict:
    """Full refresh from Databricks Superman table."""
    from databricks import sql as dbsql

    host  = os.environ["DATABRICKS_HOST"]
    path  = os.environ["DATABRICKS_HTTP_PATH"]
    token = os.environ["DATABRICKS_TOKEN"]
    table = DOCTOR_TABLE()

    where = f"WHERE {COL_DIVISION()} = '{division_filter}'" if division_filter else ""

    query = f"""
        SELECT
            {COL_ID()}        AS doctor_id,
            {COL_NAME()}      AS name,
            {COL_PHONE()}     AS whatsapp,
            {COL_EMAIL()}     AS email,
            {COL_SPECIALTY()} AS specialty,
            {COL_SUB_SPEC()}  AS sub_specialty,
            {COL_DIVISION()}  AS division,
            {COL_TIER()}      AS tier,
            {COL_HOSPITAL()}  AS hospital,
            {COL_CITY()}      AS city,
            {COL_INTERESTS()} AS interests_raw
        FROM {table}
        {where}
        ORDER BY {COL_DIVISION()}, {COL_NAME()}
    """

    with dbsql.connect(server_hostname=host, http_path=path, access_token=token) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            cols = [d[0] for d in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]

    doctors = [_map_databricks_row(r) for r in rows]
    _write_cache(doctors)
    return {"count": len(doctors), "source": "databricks"}


def _map_databricks_row(row: dict) -> dict:
    """Map a raw Databricks row to the Pinnacle portal doctor format."""
    interests_raw = row.get("interests_raw") or ""
    if isinstance(interests_raw, list):
        interests = interests_raw
    elif isinstance(interests_raw, str) and interests_raw:
        interests = [i.strip() for i in interests_raw.replace(";", ",").split(",") if i.strip()]
    else:
        interests = []

    tier = (row.get("tier") or "B").upper().strip()

    return {
        "id":            row.get("doctor_id", ""),
        "name":          row.get("name", ""),
        "whatsapp":      row.get("whatsapp", ""),
        "email":         row.get("email", ""),
        "specialty":     row.get("specialty", "General Medicine"),
        "sub_specialty": row.get("sub_specialty", ""),
        "division":      row.get("division", ""),
        "tier":          tier,
        "hospital":      row.get("hospital", ""),
        "city":          row.get("city", ""),
        "interests":     interests,
        "status":        "active",
        "source":        "databricks",
        "synced_at":     datetime.now(timezone.utc).isoformat(),
    }


def _sync_from_json(division_filter: str = None) -> dict:
    """Load doctors from local JSON cache (demo fallback)."""
    if not CACHE_PATH.exists():
        return {"count": 0, "source": "json_cache", "doctors": []}
    data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    doctors = data.get("doctors", [])
    if division_filter:
        doctors = [d for d in doctors if d.get("division", "").lower() == division_filter.lower()]
    return {"count": len(doctors), "source": "json_cache", "doctors": doctors}


def _write_cache(doctors: list) -> None:
    """Write synced doctors back to the JSON cache file."""
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total":        len(doctors),
        "source":       "databricks_sync",
        "doctors":      doctors,
    }
    CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
