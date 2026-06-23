"""
PinnacleIQ Demo Backend
========================
FastAPI server for the management demo.

Storage backend is configured via STORE_BACKEND env var:
  STORE_BACKEND=sqlite       <- default for demo (zero setup)
  STORE_BACKEND=databricks   <- production (after management approval)

The API code never touches SQLite or Databricks directly —
it only calls the store abstraction. So migration = one env var change.
"""
import sys, os, json
from pathlib import Path

# Pin the SQLite DB to this file's directory so it never drifts with CWD.
# Must be set before get_store() is called.
_HERE = Path(__file__).resolve().parent
os.environ.setdefault("SQLITE_DB_PATH", str(_HERE / "pinnacleiq_demo.db"))

# Allow importing from research_agent_system/store/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "research_agent_system"))

import threading
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io

from store import get_store
from mock_runner import run_mock_pipeline
from notifications import notify_ma_new_content, notify_ma_improvement_ready, notify_bu_content_approved
from improvement_runner import run_improvement_pipeline
from doctor_sync import sync_doctors, get_sync_status
from report_generator import generate_business_report
import scheduler as sched

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(title="PinnacleIQ Research API", version="1.0.0")

# Configure CORS: restrict to specific origins to prevent CSRF attacks
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else [
    "http://localhost:5173",      # Vite dev server (React frontend)
    "http://localhost:3000",      # Alt dev port
    "http://localhost:8010",      # Same-origin API requests
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# In production, add Railway deployment URL
if not os.getenv("VITE_FRONTEND_URL"):
    # Try to infer from environment — Railway sets RAILWAY_PUBLIC_DOMAIN
    railway_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN")
    if railway_domain:
        allowed_origins.append(f"https://{railway_domain}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

from pathlib import Path
from datetime import datetime
TOPICS_FILE   = Path(__file__).parent.parent / "topics.txt"
DOCTORS_FILE  = Path(__file__).parent.parent / "doctors.json"
FILTERS_FILE  = Path(__file__).parent.parent / "filter_suggestions.txt"


def _parse_topics_text(text: str) -> list[dict]:
    topics = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        topics.append({
            "topic": parts[0] if len(parts) > 0 else line,
            "specialty": parts[1] if len(parts) > 1 else "General Medicine",
            "therapy_area": parts[2] if len(parts) > 2 else "General",
        })
    return topics


def _read_topics() -> list[dict]:
    if not TOPICS_FILE.exists():
        raise HTTPException(404, f"topics.txt not found at {TOPICS_FILE}")
    return _parse_topics_text(TOPICS_FILE.read_text(encoding="utf-8"))


def _topic_key(topic: str, specialty: str, therapy_area: str) -> tuple[str, str, str]:
    return (
        topic.strip().casefold(),
        specialty.strip().casefold(),
        therapy_area.strip().casefold(),
    )


def _persist_topic(topic: str, specialty: str, therapy_area: str) -> bool:
    topic = topic.strip()
    specialty = (specialty or "General Medicine").strip()
    therapy_area = (therapy_area or "General").strip()
    if not topic:
        return False

    existing_text = TOPICS_FILE.read_text(encoding="utf-8") if TOPICS_FILE.exists() else ""
    existing_topics = _parse_topics_text(existing_text)
    new_key = _topic_key(topic, specialty, therapy_area)
    if any(_topic_key(item["topic"], item["specialty"], item["therapy_area"]) == new_key for item in existing_topics):
        return False

    new_line = f"{topic} | {specialty} | {therapy_area}"
    if existing_text and not existing_text.endswith(("\n", "\r")):
        existing_text += "\n"
    TOPICS_FILE.write_text(existing_text + new_line + "\n", encoding="utf-8")
    return True

# ── Filter Suggestions helpers ───────────────────────────────────────────────
# Reads/writes demo/filter_suggestions.txt  (same pattern as topics.txt)

MAX_RECENT = 5   # how many recent terms to show at the top

def _parse_filters_file() -> dict:
    """Parse filter_suggestions.txt into {section: [{value, recent, ts}]}"""
    result = {"therapy_area": [], "disease": [], "keywords": []}
    if not FILTERS_FILE.exists():
        return result

    current_section = None
    section_map = {
        "[THERAPY_AREA]": "therapy_area",
        "[DISEASE]":      "disease",
        "[KEYWORDS]":     "keywords",
    }

    for raw in FILTERS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line in section_map:
            current_section = section_map[line]
            continue
        if current_section is None:
            continue

        # Format: value  OR  value [RECENT:timestamp]
        if "[RECENT:" in line:
            idx = line.index("[RECENT:")
            value = line[:idx].strip()
            ts = line[idx + 8:].rstrip("]").strip()
        else:
            value = line
            ts = None

        result[current_section].append({
            "value": value,
            "recent": ts is not None,
            "ts": ts,
        })
    return result


def _get_filter_suggestions() -> dict:
    """Return suggestions per filter: recent terms first (top 5), then defaults."""
    raw = _parse_filters_file()
    out = {}
    for section, items in raw.items():
        recent = sorted(
            [i for i in items if i["recent"]],
            key=lambda x: x["ts"] or "",
            reverse=True,
        )[:MAX_RECENT]
        defaults = [i for i in items if not i["recent"]]

        # Deduplicate: recent wins over default with same name
        recent_vals_lower = {r["value"].lower() for r in recent}
        defaults = [d for d in defaults if d["value"].lower() not in recent_vals_lower]

        out[section] = {
            "recent":   [r["value"] for r in recent],
            "defaults": [d["value"] for d in defaults],
        }
    return out


def _add_filter_term(section: str, term: str) -> bool:
    """Append a [RECENT] term to filter_suggestions.txt. Returns True if added."""
    term = term.strip()
    if not term:
        return False

    section_header_map = {
        "therapy_area": "[THERAPY_AREA]",
        "disease":      "[DISEASE]",
        "keywords":     "[KEYWORDS]",
    }
    header = section_header_map.get(section)
    if not header:
        return False

    raw = _parse_filters_file()
    existing_lower = [i["value"].lower() for i in raw.get(section, [])]

    # If term already exists as a default, promote it to recent by adding [RECENT]
    # If term already exists as recent, update timestamp
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    new_entry = f"{term} [RECENT:{ts}]"

    text = FILTERS_FILE.read_text(encoding="utf-8") if FILTERS_FILE.exists() else ""
    lines = text.splitlines()

    # Check if term already exists anywhere in this section
    in_section = False
    found = False
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped in section_header_map.values():
            in_section = (stripped == header)
            new_lines.append(line)
            continue

        if in_section and stripped and not stripped.startswith("#"):
            # Extract value from this line
            val = stripped.split("[RECENT:")[0].strip() if "[RECENT:" in stripped else stripped
            if val.lower() == term.lower():
                # Replace with updated recent entry
                new_lines.append(new_entry)
                found = True
                continue

        new_lines.append(line)

    if not found:
        # Append at end of section
        # Find last line of the target section
        insert_idx = None
        in_section = False
        for i, line in enumerate(new_lines):
            stripped = line.strip()
            if stripped == header:
                in_section = True
                continue
            if in_section:
                if stripped in section_header_map.values():
                    # Start of next section — insert before this
                    insert_idx = i
                    break
                insert_idx = i + 1  # keep tracking last line in section

        if insert_idx is not None:
            new_lines.insert(insert_idx, new_entry)
        else:
            # Section not found or file empty — append section + entry
            new_lines.append("")
            new_lines.append(header)
            new_lines.append(new_entry)

    FILTERS_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


# ── Initialise store on startup ───────────────────────────────────────────────
# get_store() reads STORE_BACKEND env var -> returns SQLiteStore or DatabricksStore
# setup() creates tables if they don't exist (idempotent)
store = get_store()
store.setup()

# Start daily job scheduler (gracefully skips if apscheduler not installed)
try:
    sched.start_scheduler(
        sync_hour=int(os.getenv("SYNC_HOUR", "6")),
        sync_minute=int(os.getenv("SYNC_MINUTE", "30")),
        content_hour=int(os.getenv("CONTENT_HOUR", "7")),
        content_minute=int(os.getenv("CONTENT_MINUTE", "0")),
    )
except Exception as e:
    print(f"[App] Scheduler start failed: {e}")

# In-memory pipeline run status (transient — doesn't need persistence)
pipeline_runs: dict = {}
_lock = threading.Lock()

# ── Pydantic schemas ──────────────────────────────────────────────────────────
class RunRequest(BaseModel):
    topic: str
    specialty: str
    therapy_area: str

class ApproveRequest(BaseModel):
    reviewer: Optional[str] = "Dr. Prashant Agarwal (MA)"

class UpdateMetadataRequest(BaseModel):
    specialty:                  Optional[str] = None
    therapy_area:               Optional[str] = None
    sub_category:               Optional[str] = None
    tags:                       Optional[list] = None
    evidence_quality:           Optional[str] = None
    summary:                    Optional[str] = None
    relevant_doctor_specialties: Optional[str] = None

class RejectRequest(BaseModel):
    reason: str
    reviewer: Optional[str] = "Dr. Prashant Agarwal (MA)"

class ShareRequest(BaseModel):
    doctor_id:    Optional[str] = "doc_001"
    doctor_name:  Optional[str] = "Demo Doctor"
    specialty:    Optional[str] = "General Medicine"
    channel:      Optional[str] = "whatsapp"
    shared_by:    Optional[str] = "Jijo (BU Head · PMT)"

class ImprovementRequest(BaseModel):
    notes: str
    reviewer: Optional[str] = "Dr. Prashant Agarwal (MA)"


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/")
def health():
    backend = os.getenv("STORE_BACKEND", "sqlite")
    return {"status": "ok", "service": "PinnacleIQ Research API", "store": backend}


@app.get("/doctors")
def get_doctors(
    specialty: Optional[str] = None,
    city:      Optional[str] = None,
    tier:      Optional[str] = None,
    channel:   Optional[str] = None,
    q:         Optional[str] = None,       # free-text search on name / hospital
):
    """
    Return the doctor training database (100 doctors, 10 specialties).
    Filters: specialty, city, tier (A/B/C), channel (whatsapp/email), q (name search).
    Replace DOCTORS_FILE source with Databricks query once post-approval sync is live.
    """
    if not DOCTORS_FILE.exists():
        raise HTTPException(404, "doctors.json not found — run demo/generate_doctors.py first")
    data = json.loads(DOCTORS_FILE.read_text(encoding="utf-8"))
    docs = data.get("doctors", [])

    if specialty:
        docs = [d for d in docs if d["specialty"].lower() == specialty.lower()]
    if city:
        docs = [d for d in docs if d["city"].lower() == city.lower()]
    if tier:
        docs = [d for d in docs if d["tier"].upper() == tier.upper()]
    if channel:
        docs = [d for d in docs if d["preferred_channel"].lower() == channel.lower()]
    if q:
        q_lower = q.lower()
        docs = [d for d in docs if q_lower in d["name"].lower() or q_lower in d["hospital"].lower()]

    return {
        "total":      len(docs),
        "filters":    {"specialty": specialty, "city": city, "tier": tier, "channel": channel, "q": q},
        "doctors":    docs,
        "meta":       {"generated_at": data.get("generated_at"), "specialties": data.get("specialties"), "cities": data.get("cities"), "tier_breakdown": data.get("tier_breakdown")},
    }


@app.get("/doctors/{doctor_id}")
def get_doctor(doctor_id: str):
    """Return a single doctor by ID (e.g. DOC001)."""
    if not DOCTORS_FILE.exists():
        raise HTTPException(404, "doctors.json not found")
    data = json.loads(DOCTORS_FILE.read_text(encoding="utf-8"))
    doc = next((d for d in data["doctors"] if d["id"] == doctor_id.upper()), None)
    if not doc:
        raise HTTPException(404, f"Doctor {doctor_id} not found")
    return doc


@app.post("/admin/upload-doctors")
async def upload_doctors(file: UploadFile = File(...)):
    """
    Admin endpoint: upload an Excel file (.xlsx / .xls) using the DR Master Template.

    Template columns (row 1 = headers, row 2+ = data):
      Personal  (Upload):    Doctor Code, DR Name, City, Speciality, qualification, clinic address
      Superman  (CRM sync):  category, DM & DMS, SOW, MR name, Division
      Field     (Upload):    Clinical interests, Bday, Anniversary, Spouse name, No of children
      PIQ       (Derived):   engagement score, Last engaged, Next engagement, Status, preferred channel
    """
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Only .xlsx or .xls files are accepted")

    try:
        import openpyxl
    except ImportError:
        raise HTTPException(500, "openpyxl not installed — run: pip install openpyxl")

    content = await file.read()
    try:
        wb = openpyxl.load_workbook(io.BytesIO(content), data_only=True)
    except Exception as exc:
        raise HTTPException(400, f"Cannot read Excel file: {exc}")

    ws = wb.active
    if ws is None:
        raise HTTPException(400, "Excel file has no active/readable sheet")
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) < 2:
        raise HTTPException(400, "Excel file must have a header row and at least one data row")

    # Build case-insensitive, stripped column index map
    raw_headers = [
        str(h).strip().lower() if h is not None else ""
        for h in rows[0]
    ]
    col = {name: idx for idx, name in enumerate(raw_headers)}

    def _get(row, *keys, default=""):
        """Return first non-empty cell value matching any of the given header names."""
        for k in keys:
            k_low = k.lower()
            if k_low in col and col[k_low] < len(row):
                v = row[col[k_low]]
                if v is not None and str(v).strip():
                    return str(v).strip()
        return default

    def _get_num(row, *keys, default=0):
        v = _get(row, *keys, default=None)
        if v is None:
            return default
        # Handle "5000/10000" style DM&DMS — take first number
        v = str(v).split("/")[0].replace(",", "").strip()
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return default

    doctors = []
    specialties_set: set = set()
    cities_set: set = set()
    tier_count = {"A": 0, "B": 0, "C": 0}
    divisions_set: set = set()

    for i, row in enumerate(rows[1:], start=1):
        if all(v is None for v in row):
            continue  # skip blank rows

        # ── Personal fields (Upload) ──────────────────────────────────────────
        doc_id = _get(row, "doctor code", "id", "doctor_id", "doc_id")
        if not doc_id:
            doc_id = f"DOC{i:03d}"
        elif not doc_id.upper().startswith("DOC"):
            doc_id = f"DOC{doc_id}" if doc_id[:1].isdigit() else doc_id

        name = _get(row, "dr name", "doctor name", "name", "full_name") or f"Dr. Doctor {i}"
        city = _get(row, "city") or "Unknown"
        specialty = _get(row, "speciality", "specialty") or "General Medicine"
        qualification = _get(row, "qualification", "designation") or "Consultant"
        clinic_address = _get(row, "clinic address", "hospital", "hospital_name", "address") or ""

        # ── Superman / CRM fields (DB integration) ────────────────────────────
        category = _get(row, "category", "tier").upper()
        tier = category if category in ("A", "B", "C") else "B"
        dm_dms_raw = _get(row, "dm & dms", "dm&dms", "dm_dms")
        dm_val = _get_num(row, "dm & dms", "dm&dms", "dm_dms")
        sow = _get(row, "sow", "share of wallet")
        mr_name = _get(row, "mr name", "mr_name", "medical rep")
        division = _get(row, "division")

        # ── Field data (Upload) ───────────────────────────────────────────────
        clinical_interests = _get(row, "clinical interests", "sub_specialty", "subspecialty")
        birthday = _get(row, "bday", "birthday", "dob", "date of birth")
        anniversary = _get(row, "anniversary")
        spouse_name = _get(row, "spouse name", "spouse_name")
        children_raw = _get(row, "no of children", "children", "no_of_children")
        try:
            num_children = int(float(children_raw)) if children_raw else 0
        except (ValueError, TypeError):
            num_children = 0

        # ── PIQ / Derived fields ──────────────────────────────────────────────
        engagement_score = _get_num(row, "engagement score", "engagement_score")
        last_engaged = _get(row, "last engaged", "last_contacted", "last_contact")
        next_engagement = _get(row, "next engagement", "next_engagement")
        status = (_get(row, "status") or "active").lower()
        preferred_channel = (_get(row, "preferred channel", "preferred_channel", "channel") or "whatsapp").lower()

        # ── Accumulate metadata ───────────────────────────────────────────────
        specialties_set.add(specialty)
        cities_set.add(city)
        tier_count[tier] = tier_count.get(tier, 0) + 1
        if division:
            divisions_set.add(division)

        doctors.append({
            # Core identity
            "id": doc_id.upper(),
            "name": name,
            "designation": qualification,
            "specialty": specialty,
            "sub_specialty": clinical_interests or specialty,
            "hospital": clinic_address,
            "city": city,
            "state": _get(row, "state") or "",
            "tier": tier,

            # Contact
            "whatsapp": _get(row, "whatsapp", "whatsapp_number", "phone", "mobile") or "",
            "email": _get(row, "email", "email_id") or "",
            "preferred_channel": preferred_channel,

            # Superman CRM fields
            "category": category,
            "dm_dms": dm_dms_raw,
            "dm": dm_val,
            "sow": sow,
            "mr_name": mr_name,
            "division": division,

            # Clinical
            "clinical_interests": clinical_interests,
            "patients_per_day": _get_num(row, "patients per day", "patients_per_day"),
            "years_experience": _get_num(row, "years experience", "years_experience", "experience"),

            # Personal
            "birthday": birthday,
            "anniversary": anniversary,
            "spouse_name": spouse_name,
            "num_children": num_children,

            # PIQ / Derived
            "engagement_score": engagement_score,
            "pinnacle_score": _get_num(row, "pinnacle score", "pinnacle_score"),
            "last_contacted": last_engaged,
            "next_engagement": next_engagement,
            "status": status,

            # Legacy fields kept for compatibility
            "content_received": _get_num(row, "content received", "content_received"),
            "pinnacle_joined": _get(row, "pinnacle joined", "pinnacle_joined", "joined") or "",
            "notes": _get(row, "notes", "remarks") or "",
        })

    if not doctors:
        raise HTTPException(400, "No valid doctor rows found in the uploaded file")

    now = datetime.now().strftime("%Y-%m-%d")
    new_data = {
        "generated_at": now,
        "uploaded_at": now,
        "uploaded_file": file.filename,
        "total": len(doctors),
        "specialties": sorted(specialties_set),
        "cities": sorted(cities_set),
        "divisions": sorted(divisions_set),
        "tier_breakdown": tier_count,
        "doctors": doctors,
    }

    # Atomic write: write to a temp file in the same dir, then os.replace() so a
    # crash or concurrent upload can never leave doctors.json half-written/corrupt.
    _payload = json.dumps(new_data, indent=2, ensure_ascii=False)
    _tmp = DOCTORS_FILE.with_suffix(DOCTORS_FILE.suffix + ".tmp")
    _tmp.write_text(_payload, encoding="utf-8")
    os.replace(_tmp, DOCTORS_FILE)

    return {
        "success": True,
        "message": f"Doctor database updated — {len(doctors)} doctors imported from '{file.filename}'",
        "total": len(doctors),
        "specialties": sorted(specialties_set),
        "cities": sorted(cities_set),
        "divisions": sorted(divisions_set),
        "tier_breakdown": tier_count,
    }


@app.get("/topics")
def get_topics():
    """Read research topics from topics.txt."""
    topics = _read_topics()
    return {"topics": topics, "count": len(topics)}


# ── Occasions ─────────────────────────────────────────────────────────────────

_OCCASIONS = [
    {"id":"o1",  "date":"2026-05-04","name":"World Asthma Day",                "icon":"🫁","color":"#EFF6FF","c":"#1E40AF","tag":"medical",  "specialty":["Physician","Pulmonology"],                            "stat":"3 days away",  "msg":"Dear Dr. {first},\n\nWishing you a meaningful World Asthma Day! Your efforts in managing respiratory health make a real difference to patients' lives.\n\nWith warm regards,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o2",  "date":"2026-05-08","name":"World Thalassaemia Day",           "icon":"🩸","color":"#FDF2F8","c":"#9D174D","tag":"medical",  "specialty":["Haematology","Physician"],                            "stat":"7 days away",  "msg":"Dear Dr. {first},\n\nOn World Thalassaemia Day, we salute your commitment to patients living with this condition. Your dedication inspires us.\n\nWarmly,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o3",  "date":"2026-05-12","name":"International Nurses Day",         "icon":"💉","color":"#ECFDF5","c":"#065F46","tag":"medical",  "specialty":None,                                                   "stat":"11 days away", "msg":"Dear Dr. {first},\n\nHappy International Nurses Day! A moment to appreciate the incredible teams you lead and the care they provide every day.\n\nWith gratitude,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o4",  "date":"2026-06-01","name":"World Milk Day",                   "icon":"🥛","color":"#FFFBEB","c":"#92400E","tag":"medical",  "specialty":["Paediatrics","Gynaecology","General Medicine"],       "stat":"This month",   "msg":"Dear Dr. {first},\n\nHappy World Milk Day! Nutrition starts early — a reminder of the foundational role you play in guiding families toward healthier futures.\n\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o5",  "date":"2026-06-14","name":"World Blood Donor Day",            "icon":"❤️","color":"#FEF2F2","c":"#991B1B","tag":"medical",  "specialty":["Haematology","Cardiology","General Medicine"],        "stat":"This month",   "msg":"Dear Dr. {first},\n\nOn World Blood Donor Day, we recognise your crucial role in promoting safe transfusion practices and patient care.\n\nWith respect,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o6",  "date":"2026-07-01","name":"Doctors' Day",                     "icon":"👨‍⚕️","color":"linear-gradient(135deg,#EBF0F8,#DBEAFE)","c":"var(--navy)","tag":"national","specialty":None,"featured":True,"stat":"Next month",   "msg":"Dear Dr. {first},\n\nHappy National Doctors' Day! 🎉\n\nThank you for your tireless dedication, your healing hands and your compassionate care. Mankind Pharma is proud to partner with you in your mission.\n\nWith deep gratitude and respect,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o7",  "date":"2026-07-28","name":"World Hepatitis Day",              "icon":"🟡","color":"#FFFBEB","c":"#92400E","tag":"medical",  "specialty":["Gastroenterology","General Medicine"],                "stat":"July",         "msg":"Dear Dr. {first},\n\nOn World Hepatitis Day, we appreciate your work in diagnosis and management. Your clinical expertise is vital in the fight against viral hepatitis.\n\nWarmly,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o8",  "date":"2026-08-12","name":"World Organ Donation Day",         "icon":"🫀","color":"#FDF2F8","c":"#9D174D","tag":"medical",  "specialty":["Cardiology","Physician"],                             "stat":"August",       "msg":"Dear Dr. {first},\n\nOn World Organ Donation Day, we salute your role in supporting life-saving interventions and educating patients on the gift of life.\n\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o9",  "date":"2026-09-29","name":"World Heart Day",                  "icon":"💓","color":"#FEF2F2","c":"#991B1B","tag":"medical",  "specialty":["Cardiology","General Medicine"],                      "stat":"September",    "msg":"Dear Dr. {first},\n\nHappy World Heart Day! Your dedication to cardiovascular health saves lives every day. We are proud to support your practice.\n\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o10", "date":"2026-10-02","name":"Gandhi Jayanti",                   "icon":"🇮🇳","color":"#ECFDF5","c":"#065F46","tag":"national", "specialty":None,                                                  "stat":"October",      "msg":"Dear Dr. {first},\n\nOn the occasion of Gandhi Jayanti, wishing you peace, purpose and continued service to the nation's health.\n\nWith warm regards,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o11", "date":"2026-10-20","name":"Diwali",                           "icon":"🪔","color":"#FFFBEB","c":"#92400E","tag":"national", "specialty":None, "featured":True,                                  "stat":"October",      "msg":"Dear Dr. {first},\n\nWishing you and your family a very Happy Diwali! 🪔✨\n\nMay this festival of lights illuminate your life with joy, good health and prosperity.\n\nWith warm Diwali wishes,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o12", "date":"2026-11-14","name":"Children's Day / World Diabetes Day","icon":"🩺","color":"#EFF6FF","c":"#1E40AF","tag":"medical","specialty":["Paediatrics","Diabetology","Endocrinology"],          "stat":"November",     "msg":"Dear Dr. {first},\n\nOn World Diabetes Day, we acknowledge your pivotal role in managing and preventing diabetes across generations. Your patient-first approach sets the standard.\n\nWith admiration,\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o13", "date":"2026-12-01","name":"World AIDS Day",                   "icon":"🎗️","color":"#FDF2F8","c":"#9D174D","tag":"medical",  "specialty":["General Medicine","Physician"],                       "stat":"December",     "msg":"Dear Dr. {first},\n\nOn World AIDS Day, we stand with you in the fight against HIV/AIDS and commend your work in patient care and awareness.\n\n— Jijo, Team Life · Mankind Pharma"},
    {"id":"o14", "date":"2027-03-14","name":"Holi",                             "icon":"🎨","color":"#F5F3FF","c":"#5B21B6","tag":"national", "specialty":None,                                                  "stat":"March 2027",   "msg":"Dear Dr. {first},\n\nWishing you and your family a vibrant and joyful Holi! 🎨\n\nMay the colours of good health, happiness and success fill your life this season.\n\nWith colourful wishes,\n— Jijo, Team Life · Mankind Pharma"},
]

@app.get("/occasions")
def get_occasions():
    """Return the occasions calendar for the Occasion Hub."""
    return {"occasions": _OCCASIONS, "count": len(_OCCASIONS)}


# ── Filter Suggestions endpoints ─────────────────────────────────────────────

@app.get("/filters/suggestions")
def get_filter_suggestions():
    """
    Return autocomplete suggestions for Research Agent filter fields.
    Each section returns { recent: [...top 5], defaults: [...] }.
    Recent terms are sorted by most-recently-used first.
    """
    return _get_filter_suggestions()


class AddFilterTermRequest(BaseModel):
    section: str    # therapy_area | disease | keywords
    term: str       # the value to add

@app.post("/filters/suggestions")
def add_filter_suggestion(req: AddFilterTermRequest):
    """
    Add a user-searched term to filter_suggestions.txt.
    Term is tagged [RECENT] and will appear at the top of the dropdown.
    Only the 5 most recent terms per section are shown at top.
    """
    valid_sections = ["therapy_area", "disease", "keywords"]
    if req.section not in valid_sections:
        raise HTTPException(400, f"Invalid section '{req.section}'. Must be one of: {valid_sections}")
    if not req.term.strip():
        raise HTTPException(400, "Term cannot be empty")

    added = _add_filter_term(req.section, req.term.strip())
    return {
        "added": added,
        "section": req.section,
        "term": req.term.strip(),
        "message": f"Term '{req.term.strip()}' {'added to' if added else 'updated in'} {req.section}",
    }


@app.post("/pipeline/run")
def start_pipeline(req: RunRequest, bg: BackgroundTasks):
    """Start mock pipeline in background. Returns run_id for polling."""
    from datetime import datetime, timezone

    # Persist custom topics so they remain available after refreshes and future runs.
    with _lock:
        _persist_topic(req.topic, req.specialty, req.therapy_area)

    run_id = str(uuid.uuid4())
    with _lock:
        pipeline_runs[run_id] = {
            "status":        "running",
            "topic":         req.topic,
            "specialty":     req.specialty,
            "progress":      0,
            "current_agent": "alpha",
            "status_msg":    "Starting pipeline...",
            "content_id":    None,
            "improvement":   False,
            "started_at":    datetime.now(timezone.utc).isoformat(),
        }

    def _run():
        run_mock_pipeline(
            topic=req.topic,
            specialty=req.specialty,
            therapy_area=req.therapy_area,
            run_store=pipeline_runs,
            run_id=run_id,
        )
        # Persist completed content via the store abstraction
        # Save ALL cards (one per paper) to SQLite
        run = pipeline_runs.get(run_id, {})
        if run.get("status") == "completed":
            all_cards = run.get("all_cards", [])
            if not all_cards and run.get("content"):
                all_cards = [run["content"]]  # backward compat: single card

            saved_ids = []
            for card in all_cards:
                try:
                    cid = store.save_content_card(card)
                    saved_ids.append(cid)
                    print(f"[App] Saved card: {card.get('title','')[:60]}... → {cid}")
                except Exception as e:
                    print(f"[App] Failed to save card: {e}")

            pipeline_runs[run_id]["content_id"] = saved_ids[0] if saved_ids else None
            pipeline_runs[run_id]["all_content_ids"] = saved_ids
            print(f"[App] Pipeline saved {len(saved_ids)} card(s) to SQLite")

            # Notify MA team that new content is ready for review
            try:
                first_card = all_cards[0] if all_cards else run.get("content", {})
                notify_ma_new_content(
                    store,
                    saved_ids[0] if saved_ids else "",
                    first_card.get("title", req.topic),
                    req.specialty,
                    first_card.get("division", "All"),
                )
            except Exception as e:
                print(f"[App] Pipeline notification failed: {e}")

    bg.add_task(_run)
    return {"run_id": run_id, "status": "running"}


@app.get("/pipeline/status/{run_id}")
def pipeline_status(run_id: str):
    """Poll for pipeline progress (0-100%)."""
    run = pipeline_runs.get(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return {
        "run_id":         run_id,
        "status":         run["status"],
        "progress":       run["progress"],
        "current_agent":  run["current_agent"],
        "status_msg":     run["status_msg"],
        "content_id":     run.get("content_id"),
        "all_content_ids": run.get("all_content_ids", []),
        "agent_outputs":  run.get("agent_outputs", {}),
    }


@app.get("/pipeline/runs")
def get_pipeline_runs(limit: int = 30):
    """
    Return recent pipeline runs — both new research runs and improvement re-runs.
    Used by the Research Pipeline page to show activity history.
    """
    runs = []
    for run_id, run in pipeline_runs.items():
        runs.append({
            "run_id":        run_id,
            "type":          "improvement" if run.get("improvement") else "new",
            "topic":         run.get("topic", "Unknown"),
            "specialty":     run.get("specialty", ""),
            "status":        run.get("status", "unknown"),
            "progress":      run.get("progress", 0),
            "current_agent": run.get("current_agent", ""),
            "status_msg":    run.get("status_msg", ""),
            "content_id":    run.get("content_id"),
            "original_id":   run.get("original_id"),
            "version":       run.get("version"),
            "started_at":    run.get("started_at", ""),
        })
    # Most recent first (insertion order reversed)
    runs.reverse()
    return {"runs": runs[:limit], "total": len(runs)}


@app.get("/content")
def list_content(status: Optional[str] = None, specialty: Optional[str] = None):
    """List all content items with optional filters."""
    items = store.list_content(status=status, specialty=specialty)
    return {
        "items": items,
        "counts": {
            "total":    len(items),
            "pending":  sum(1 for i in items if i.get("status") == "pending_review"),
            "approved": sum(1 for i in items if i.get("status") == "approved"),
            "rejected": sum(1 for i in items if i.get("status") == "rejected"),
        },
    }


@app.get("/content/{content_id}")
def get_content(content_id: str):
    """Get a single content item."""
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    return item


@app.post("/content/{content_id}/approve")
def approve_content(content_id: str, req: ApproveRequest):
    """MA approves a content card."""
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    store.approve(content_id, reviewer=req.reviewer)
    # Only notify BU Head when moving from pending → approved (not on re-approve)
    if item.get("status") in ("pending_review", "improvement_requested"):
        try:
            notify_bu_content_approved(
                store,
                content_id,
                item.get("title", content_id),
                item.get("division", "All"),
            )
        except Exception as e:
            print(f"[App] Approval notification failed: {e}")
    return {"message": "Content approved. Now available for BU Head to share.", "content_id": content_id}


@app.patch("/content/{content_id}")
def update_content_metadata(content_id: str, req: UpdateMetadataRequest):
    """MA edits categorisation fields (specialty, therapy_area, sub_category, tags, etc.)
    on any card regardless of status. Separate from approve/reject workflow."""
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    fields = {k: v for k, v in req.model_dump().items() if v is not None}
    updated = store.update_metadata(content_id, fields)
    if not updated:
        raise HTTPException(400, "No valid fields to update")
    return {"message": "Content metadata updated.", "content_id": content_id, "updated_fields": list(fields.keys())}


@app.post("/content/{content_id}/reject")
def reject_content(content_id: str, req: RejectRequest):
    """MA rejects a content card with a reason."""
    if not req.reason.strip():
        raise HTTPException(400, "Rejection reason is required")
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    store.reject(content_id, reason=req.reason, reviewer=req.reviewer)
    return {"message": "Content rejected.", "content_id": content_id}


@app.post("/content/{content_id}/share")
def share_content(content_id: str, req: ShareRequest):
    """BU Head shares content with a doctor.
    Note: approval check removed — sharing and MA approval are independent workflows.
    PMT can share any pipeline-generated content.
    Accepts both API-sourced (UUID) and static (static-N) content IDs."""
    result = store.log_share(
        content_id=content_id,
        doctor_id=req.doctor_id,
        doctor_name=req.doctor_name,
        doctor_specialty=req.specialty,
        channel=req.channel,
        shared_by=req.shared_by,
    )
    return {
        "message": f"Content shared via {req.channel} with {req.doctor_name}.",
        "log_id":  result["log_id"],
        "warning": result["warning"],
    }


@app.get("/share-logs")
def get_share_logs(content_id: Optional[str] = None):
    """Return sharing history."""
    return {"logs": store.get_share_logs(content_id=content_id)}


# ── Improvement (HITL) endpoints ──────────────────────────────────────────────

@app.post("/content/{content_id}/request-improvement")
def request_improvement(content_id: str, req: ImprovementRequest, bg: BackgroundTasks):
    """
    MA requests improvement on a content card.
    Sets status to 'improvement_requested', then runs Beta+Gamma re-run in background.
    Returns run_id for polling via /pipeline/status/{run_id}.
    """
    if not req.notes or not req.notes.strip():
        raise HTTPException(400, "Improvement notes are required")

    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    # Allow improvement on pending_review, improvement_requested, AND rejected content
    if item.get("status") not in ("pending_review", "improvement_requested", "rejected"):
        raise HTTPException(400, f"Content status is '{item.get('status')}' — cannot request improvement")

    # Mark as improvement_requested in the DB
    store.request_improvement(content_id, notes=req.notes, reviewer=req.reviewer)

    # Start improvement pipeline in background
    from datetime import datetime, timezone
    run_id = str(uuid.uuid4())
    with _lock:
        pipeline_runs[run_id] = {
            "status":        "running",
            "topic":         item.get("topic", ""),
            "specialty":     item.get("specialty", ""),
            "progress":      0,
            "current_agent": "alpha",
            "status_msg":    "Starting improvement pipeline...",
            "content_id":    None,
            "improvement":   True,
            "original_id":   content_id,
            "started_at":    datetime.now(timezone.utc).isoformat(),
        }

    def _run_improvement():
        run_improvement_pipeline(
            original_content=item,
            improvement_notes=req.notes,
            run_store=pipeline_runs,
            run_id=run_id,
            store=store,
            notify_fn=notify_ma_improvement_ready,
        )

    bg.add_task(_run_improvement)
    return {
        "run_id":      run_id,
        "status":      "running",
        "message":     "Improvement pipeline started. Poll /pipeline/status/{run_id} for progress.",
        "content_id":  content_id,
    }


@app.get("/content/{content_id}/versions")
def get_content_versions(content_id: str):
    """Return all versions of a content card (original + improvements)."""
    item = store.get_content(content_id)
    if not item:
        raise HTTPException(404, "Content not found")
    # Resolve root ID — if this card is itself a revision, find the root
    root_id = item.get("parent_id") or content_id
    versions = store.get_content_versions(root_id)
    return {
        "root_id":  root_id,
        "versions": versions,
        "count":    len(versions),
    }


# ── Notification endpoints ────────────────────────────────────────────────────

@app.get("/notifications")
def get_notifications(
    division: Optional[str] = None,
    unread_only: bool = False,
):
    """Return in-app notifications, optionally filtered by division or unread status."""
    notifications = store.get_notifications(division=division, unread_only=unread_only)
    unread_count = sum(1 for n in notifications if not n.get("read_at"))
    return {
        "notifications": notifications,
        "total":         len(notifications),
        "unread":        unread_count,
    }


@app.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str):
    """Mark a notification as read."""
    store.mark_notification_read(notification_id)
    return {"message": "Notification marked as read", "notification_id": notification_id}


# ── Scheduler endpoints ───────────────────────────────────────────────────────

@app.get("/scheduler/status")
def scheduler_status():
    """Return the scheduler running state and list of scheduled jobs."""
    return {
        **sched.get_scheduler_status(),
        "job_history": sched.get_job_history()[:10],  # last 10 entries
    }


@app.post("/scheduler/run-now/{job_name}")
def run_job_now(job_name: str):
    """Manually trigger a scheduled job immediately (doctor_sync or content_generation)."""
    result = sched.run_job_now(job_name)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return {"message": f"Job '{job_name}' triggered in background", **result}


# ── Doctor sync endpoint ──────────────────────────────────────────────────────

@app.post("/sync/doctors")
def sync_doctors_endpoint(division: Optional[str] = None):
    """
    Manual doctor sync trigger.
    Pulls from Databricks Superman CRM table (or falls back to JSON cache in demo mode).
    """
    result = sync_doctors(division_filter=division)
    return {
        "message":      f"Doctor sync complete — {result['count']} doctors loaded",
        "count":        result["count"],
        "source":       result["source"],
        "duration_sec": result.get("duration_sec", 0),
        "sync_status":  get_sync_status(),
    }


@app.get("/sync/doctors/status")
def doctor_sync_status():
    """Return the last doctor sync status."""
    return get_sync_status()



# ── Business Report ──────────────────────────────────────────────────────────

@app.get("/report/download")
def download_business_report(
    status: Optional[str] = None,
    specialty: Optional[str] = None,
    therapy_area: Optional[str] = None,
    disease: Optional[str] = None,
    keywords: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    """
    Generate and download the PinnacleIQ Research Report as an Excel file.
    Optional filters: status, specialty, therapy_area, disease, keywords, date_from, date_to.
    """
    from datetime import datetime, timezone

    items = store.list_content(status=status, specialty=specialty, limit=10000)
    if not items:
        raise HTTPException(404, "No content items found for the given filters.")

    # Build search summary data
    search_params = {
        'therapy_area': therapy_area or 'All',
        'disease': disease or 'All',
        'keywords': keywords or 'None selected',
        'date_from': date_from or '2024-01-01',
        'date_to': date_to or '2026-06-01',
    }

    buf = generate_business_report(items, search_params)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = f"PinnacleIQ_PubMed_Database_{date_str}.xlsx"

    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Serve portal HTML ─────────────────────────────────────────────────────────
from fastapi.responses import FileResponse as _FileResponse

PORTAL_HTML = Path(__file__).parent.parent.parent / "PinnacleIQ_Portal.html"

@app.get("/portal", include_in_schema=False)
@app.get("/app",    include_in_schema=False)
async def serve_portal():
    if PORTAL_HTML.exists():
        return _FileResponse(str(PORTAL_HTML), media_type="text/html")
    return {"error": "Portal HTML not found at " + str(PORTAL_HTML)}


# ── Serve React SPA (for production/Railway deployment) ───────────────────────
from fastapi.staticfiles import StaticFiles

REACT_DIST = Path(__file__).parent.parent.parent / "react-app" / "dist"

if REACT_DIST.exists():
    # Serve JS/CSS/assets
    app.mount("/assets", StaticFiles(directory=str(REACT_DIST / "assets")), name="assets")

    @app.get("/", include_in_schema=False)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str = ""):
        # Let API routes pass through (they are registered before this catch-all)
        index = REACT_DIST / "index.html"
        if index.exists():
            return _FileResponse(str(index))
        return {"error": "React build not found. Run: cd react-app && npm run build"}


if __name__ == "__main__":
    import uvicorn
    import sys
    # Railway (and other PaaS) set PORT env var — fall back to CLI arg, then 8010
    port = int(
        os.environ.get("PORT") or
        (sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8010)
    )
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
