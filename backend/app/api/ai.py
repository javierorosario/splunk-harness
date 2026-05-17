from fastapi import APIRouter

from app.schemas.ai import AiInvestigationRequest
from app.services.ai_investigator import investigate
from app.utils.redaction import redact


router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.post("/investigate")
def investigate_evidence(request: AiInvestigationRequest) -> dict:
    return redact(
        investigate(
            {
                "instance": request.instance,
                "forwarder_status": request.forwarder_status,
                "splunk_validation": request.splunk_validation,
                "evidence_context": request.evidence_context,
            }
        )
    )
