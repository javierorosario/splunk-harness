from app.config import Settings
from app.services.splunk_client import SplunkClient


def build_validation_query(instance_id: str, hostname: str | None, index: str, sourcetype: str | None) -> str:
    filters = [f'index="{index}"']
    if hostname:
        filters.append(f'host="{hostname}"')
    if sourcetype:
        filters.append(f'sourcetype="{sourcetype}"')
    filters.append(f'("{instance_id}" OR host=*)')
    return "search " + " ".join(filters) + " earliest=-30m | head 5"


def validate_ingestion(
    settings: Settings,
    instance_id: str,
    hostname: str | None,
    index: str | None,
    sourcetype: str | None,
) -> dict:
    selected_index = index or settings.splunk_default_index
    query = build_validation_query(instance_id, hostname, selected_index, sourcetype)
    result = SplunkClient(settings).search_oneshot(query)
    rows = result.get("results", [])
    return {
        "status": "validated" if rows else "not_found",
        "telemetry_found": bool(rows),
        "query": query,
        "evidence": {"sample_count": len(rows), "samples": rows[:5]},
    }
