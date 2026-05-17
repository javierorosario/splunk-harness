from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.schemas.workflows import ForwarderInstallRequest, InstanceRequest
from app.services.ssm_runner import check_forwarder, install_forwarder_placeholder
from app.utils.redaction import redact


router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/check-forwarder")
def check_forwarder_status(request: InstanceRequest, settings: Settings = Depends(get_settings)) -> dict:
    try:
        result = check_forwarder(settings, request.instance_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return redact({"instance_id": request.instance_id, "status": result["status"], "evidence": result})


@router.post("/install-forwarder")
def install_forwarder(request: ForwarderInstallRequest, settings: Settings = Depends(get_settings)) -> dict:
    if not request.options.approved:
        raise HTTPException(status_code=400, detail="Operator approval is required before SSM install/configure workflow starts.")

    try:
        result = install_forwarder_placeholder(settings, request.instance_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return redact({"instance_id": request.instance_id, "status": result["status"], "evidence": result})
