from fastapi import APIRouter, Depends

from app.config import Settings, get_settings


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict:
    return {
        "service": settings.app_name,
        "status": "ok",
        "aws_configured": settings.aws_configured,
        "splunk_configured": settings.splunk_configured,
        "ai_provider": settings.ai_provider,
    }
