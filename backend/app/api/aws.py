from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.schemas.aws import InstanceListResponse
from app.services.cloud_discovery import discover_provider_resources


router = APIRouter(prefix="/api/aws", tags=["aws"])


@router.get("/instances", response_model=InstanceListResponse)
def instances(settings: Settings = Depends(get_settings)) -> dict:
    try:
        discovered = discover_provider_resources(settings, "aws")
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return discovered
