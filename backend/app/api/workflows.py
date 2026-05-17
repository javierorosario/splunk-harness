from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.schemas.workflows import ForwarderInstallRequest, InstanceRequest
from app.services.manual_runner import manual_forwarder_check, manual_forwarder_install
from app.services.ssh_runner import check_forwarder_ssh, install_forwarder_ssh
from app.services.ssm_runner import check_forwarder, install_forwarder_placeholder
from app.utils.redaction import redact


router = APIRouter(prefix="/api/workflows", tags=["workflows"])


@router.post("/check-forwarder")
def check_forwarder_status(request: InstanceRequest, settings: Settings = Depends(get_settings)) -> dict:
    method = request.execution_method.lower()
    if method == "ssh":
        result = check_forwarder_ssh(settings, request.host, request.ssh_username, request.ssh_port)
    elif method == "ssm":
        try:
            result = check_forwarder(settings, request.instance_id)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    elif method == "manual":
        result = manual_forwarder_check(request.instance_id, request.host)
    else:
        raise HTTPException(status_code=400, detail="Unsupported execution method. Use ssh, ssm, or manual.")
    return redact({"instance_id": request.instance_id, "status": result["status"], "evidence": result})


@router.post("/install-forwarder")
def install_forwarder(request: ForwarderInstallRequest, settings: Settings = Depends(get_settings)) -> dict:
    if not request.options.approved:
        raise HTTPException(status_code=400, detail="Operator approval is required before install/configure workflow starts.")

    method = request.execution_method.lower()
    if method == "ssh":
        result = install_forwarder_ssh(settings, request.host, request.ssh_username, request.ssh_port)
    elif method == "ssm":
        try:
            result = install_forwarder_placeholder(settings, request.instance_id)
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    elif method == "manual":
        result = manual_forwarder_install(request.instance_id, request.host)
    else:
        raise HTTPException(status_code=400, detail="Unsupported execution method. Use ssh, ssm, or manual.")
    return redact({"instance_id": request.instance_id, "status": result["status"], "evidence": result})
