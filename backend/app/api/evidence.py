from fastapi import APIRouter

from app.schemas.evidence import EvidenceGenerateRequest
from app.services.evidence_builder import generate_bundle


router = APIRouter(prefix="/api/evidence", tags=["evidence"])


@router.post("/generate")
def generate(request: EvidenceGenerateRequest) -> dict:
    return generate_bundle(request.model_dump())
