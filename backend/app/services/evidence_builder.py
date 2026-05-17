import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.utils.redaction import redact


EVIDENCE_DIR = Path(__file__).resolve().parents[1] / "storage" / "evidence"


def generate_bundle(payload: dict) -> dict:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    created_at = datetime.now(UTC).isoformat()
    bundle_id = f"evidence-{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}-{uuid4().hex[:8]}"
    bundle = redact(
        {
            "bundle_id": bundle_id,
            "created_at": created_at,
            "workflow": "splunk_forwarder_onboarding",
            **payload,
        }
    )
    path = EVIDENCE_DIR / f"{bundle_id}.json"
    path.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    return {"bundle_id": bundle_id, "path": str(path), "bundle": bundle}
