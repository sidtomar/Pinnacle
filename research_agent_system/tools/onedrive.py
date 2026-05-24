"""
OneDrive file reader tool using Microsoft Graph API + MSAL.

Supports: .txt, .pdf, .docx, .xlsx files.
Auth: Client-credentials flow (app-only, no user login needed).
"""
import io
import os
from typing import Any

import msal
import requests
from langchain_core.tools import tool

_GRAPH_BASE = "https://graph.microsoft.com/v1.0"


def _get_access_token() -> str:
    """Acquire an app-only access token via MSAL."""
    app = msal.ConfidentialClientApplication(
        client_id=os.environ["ONEDRIVE_CLIENT_ID"],
        client_credential=os.environ["ONEDRIVE_CLIENT_SECRET"],
        authority=f"https://login.microsoftonline.com/{os.environ['ONEDRIVE_TENANT_ID']}",
    )
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )
    if "access_token" not in result:
        raise RuntimeError(f"MSAL auth failed: {result.get('error_description')}")
    return result["access_token"]


def _graph_get(path: str, token: str, stream: bool = False) -> Any:
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(f"{_GRAPH_BASE}{path}", headers=headers, stream=stream, timeout=30)
    r.raise_for_status()
    return r if stream else r.json()


def _extract_text(content: bytes, filename: str) -> str:
    """Extract plain text from supported file types."""
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".txt":
        return content.decode("utf-8", errors="replace")

    if ext == ".pdf":
        import PyPDF2

        reader = PyPDF2.PdfReader(io.BytesIO(content))
        return "\n".join(p.extract_text() or "" for p in reader.pages)

    if ext == ".docx":
        from docx import Document

        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs)

    if ext == ".xlsx":
        import openpyxl

        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        lines = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                lines.append("\t".join(str(c) if c is not None else "" for c in row))
        return "\n".join(lines)

    return f"[Unsupported file type: {ext}]"


@tool
def read_onedrive_files(query: str) -> str:
    """
    Search OneDrive for files matching the query in the configured folder and
    return their text content.

    Input: a topic or keyword to match against file names.
    Output: concatenated text content of all matched files.
    """
    # Gracefully skip if OneDrive credentials are not configured
    if not all([
        os.getenv("ONEDRIVE_CLIENT_ID"),
        os.getenv("ONEDRIVE_CLIENT_SECRET"),
        os.getenv("ONEDRIVE_TENANT_ID"),
    ]):
        return "OneDrive not configured — no internal documents searched."

    folder_path = os.getenv("ONEDRIVE_FOLDER_PATH", "Research")
    token = _get_access_token()

    # Resolve the folder by path in the signed-in user's default drive
    search_url = f"/me/drive/root:/{folder_path}:/children"
    try:
        items = _graph_get(search_url, token)
    except requests.HTTPError:
        # Fall back to root if folder not found
        items = _graph_get("/me/drive/root/children", token)

    files = [
        i for i in items.get("value", [])
        if i.get("file") and query.lower() in i["name"].lower()
    ]

    if not files:
        return f"No files found in OneDrive folder '{folder_path}' matching '{query}'."

    results = []
    for f in files[:5]:  # cap at 5 files per query
        dl_url = f["@microsoft.graph.downloadUrl"]
        r = requests.get(dl_url, timeout=60)
        r.raise_for_status()
        text = _extract_text(r.content, f["name"])
        results.append(f"=== {f['name']} ===\n{text[:4000]}")  # truncate large files

    return "\n\n".join(results)
