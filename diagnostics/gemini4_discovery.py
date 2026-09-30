"""Metadata-only discovery for Gemini 4 Argon. No inference requests."""
from __future__ import annotations
import hashlib
import json
import os
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "gemini4-argon-discovery"
BASE = "https://generativelanguage.googleapis.com/v1beta/models"
TERMS = ("gemini-4", "gemini 4", "argon")
MAX_PAGES = 10
MAX_BYTES = 1_048_576

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req: Any, fp: Any, code: int, msg: str,
                         headers: Any, newurl: str) -> None:
        return None

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def request_page(url: str, key: str) -> dict[str, Any]:
    headers = {"x-goog-api-key": key, "Accept": "application/json"}
    req = urllib.request.Request(url, headers=headers, method="GET")
    with urllib.request.build_opener(NoRedirect()).open(req, timeout=20) as response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("RESPONSE_TOO_LARGE")
        if response.status != 200:
            raise ValueError("HTTP_STATUS_INVALID")
    body = json.loads(raw)
    if not isinstance(body, dict) or not isinstance(body.get("models"), list):
        raise ValueError("MODEL_LIST_SCHEMA_INVALID")
    return body

def model_view(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": item.get("name"),
        "displayName": item.get("displayName"),
        "supportedGenerationMethods": item.get("supportedGenerationMethods", []),
        "inputTokenLimit": item.get("inputTokenLimit"),
        "outputTokenLimit": item.get("outputTokenLimit"),
    }

def select_matches(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matches = []
    for item in models:
        text = " ".join(str(item.get(k, "")) for k in ("name", "displayName", "description")).lower()
        if any(term in text for term in TERMS):
            matches.append(model_view(item))
    return matches

def collect(key: str) -> tuple[list[dict[str, Any]], int]:
    models: list[dict[str, Any]] = []
    token = ""
    for _ in range(MAX_PAGES):
        query = {"pageSize": "1000"}
        if token:
            query["pageToken"] = token
        body = request_page(BASE + "?" + urllib.parse.urlencode(query), key)
        models.extend(x for x in body["models"] if isinstance(x, dict))
        token = str(body.get("nextPageToken", ""))
        if not token:
            return models, len(models)
    raise ValueError("PAGINATION_BOUND_EXCEEDED")

def write_ledger(receipt: dict[str, Any]) -> None:
    db = sqlite3.connect(OUT / "gates.sqlite")
    db.execute("CREATE TABLE cumulative_gate_ledger(timestamp TEXT,task TEXT,gate_id TEXT,requirement TEXT,status TEXT,evidence_ref TEXT,evidence_hash_reason TEXT)")
    db.execute("CREATE TABLE reverse_rca_ledger(timestamp TEXT,incident_id TEXT,checkpoint TEXT,observed_state TEXT,causal_evidence TEXT,validation_test TEXT,disposition TEXT)")
    status = receipt["status"]
    db.execute("INSERT INTO cumulative_gate_ledger VALUES (?,?,?,?,?,?,?)",
               (now(),"Gemini 4 discovery","G-GEM4-DISCOVERY-001","Authenticated metadata enumeration",status,
                "receipt.json",digest(receipt)))
    if status != "PASS":
        db.execute("INSERT INTO reverse_rca_ledger VALUES (?,?,?,?,?,?,?)",
                   (now(),"GEM4-DISCOVERY-001","Provider catalog",receipt["reason"],
                    "Authenticated model list contained no Gemini 4/Argon match",
                    "Re-run only after a new user-authorized discovery window",
                    "INVESTIGATION_COMPLETE; REQUIRES_OPERATOR_ESCALATION"))
    db.commit()
    (OUT / "gates.sql").write_text("\n".join(db.iterdump()) + "\n", encoding="utf-8")
    db.close()

def main() -> int:
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise SystemExit("HOLD:MISSING_GEMINI_API_KEY")
    OUT.mkdir(parents=True, exist_ok=False)
    try:
        models, count = collect(key)
        matches = select_matches(models)
        receipt = {"utc": now(), "scope": "metadata_only_no_inference", "requests_max": MAX_PAGES,
                   "retries": 0, "models_enumerated": count, "matches": matches,
                   "status": "PASS" if matches else "HOLD",
                   "reason": "MODEL_DISCOVERED" if matches else "MODEL_NOT_EXPOSED_TO_API_KEY"}
    except (urllib.error.URLError, TimeoutError) as exc:
        receipt = {"utc": now(), "scope": "metadata_only_no_inference", "requests_max": MAX_PAGES,
                   "retries": 0, "models_enumerated": 0, "matches": [], "status": "HOLD",
                   "reason": type(exc).__name__}
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_ledger(receipt)
    files = sorted(x for x in OUT.iterdir() if x.is_file() and x.name != "SHA256SUMS.txt")
    (OUT / "SHA256SUMS.txt").write_text("".join(hashlib.sha256(x.read_bytes()).hexdigest() + "  " + x.name + "\n" for x in files), encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
