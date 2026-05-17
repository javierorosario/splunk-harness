import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from app.utils.redaction import redact


CONNECTION_DIR = Path(__file__).resolve().parents[1] / "storage" / "connections"


def save_connection(payload: dict) -> dict:
    CONNECTION_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    connection_id = payload.get("connection_id") or f"conn-{uuid4().hex[:10]}"
    record = redact(
        {
            "connection_id": connection_id,
            "created_at": payload.get("created_at") or now,
            **payload,
        }
    )
    path = CONNECTION_DIR / f"{connection_id}.json"
    path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record


def list_connections() -> list[dict]:
    if not CONNECTION_DIR.exists():
        return []
    records = []
    for path in sorted(CONNECTION_DIR.glob("*.json")):
        records.append(json.loads(path.read_text(encoding="utf-8")))
    return records
