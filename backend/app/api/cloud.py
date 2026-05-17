from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.schemas.aws import InstanceListResponse
from app.services.cloud_discovery import discover_provider_resources


router = APIRouter(prefix="/api/cloud", tags=["cloud"])


@router.get("/{provider}/resources", response_model=InstanceListResponse)
def provider_resources(provider: str, settings: Settings = Depends(get_settings)) -> dict:
    try:
        return discover_provider_resources(settings, provider)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
