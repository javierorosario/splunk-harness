from fastapi import APIRouter, Depends, HTTPException
from requests import RequestException

from app.config import Settings, get_settings
from app.schemas.splunk import SplunkValidationRequest
from app.services.telemetry_validator import validate_ingestion
from app.utils.redaction import redact


router = APIRouter(prefix="/api/splunk", tags=["splunk"])


@router.post("/validate-ingestion")
def validate(request: SplunkValidationRequest, settings: Settings = Depends(get_settings)) -> dict:
    try:
        result = validate_ingestion(
            settings=settings,
            instance_id=request.instance_id,
            hostname=request.hostname,
            index=request.index,
            sourcetype=request.sourcetype,
        )
    except (RuntimeError, RequestException) as exc:
        raise HTTPException(status_code=503, detail=f"Splunk validation failed: {exc}") from exc
    return redact(result)
