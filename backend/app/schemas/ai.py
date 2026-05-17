from typing import Any

from pydantic import BaseModel, Field


class AiInvestigationRequest(BaseModel):
    instance: dict[str, Any] = Field(default_factory=dict)
    forwarder_status: dict[str, Any] = Field(default_factory=dict)
    splunk_validation: dict[str, Any] = Field(default_factory=dict)
    evidence_context: dict[str, Any] = Field(default_factory=dict)


class AiInvestigationResult(BaseModel):
    summary: str
    findings: list[str]
    recommended_next_actions: list[str]
    cited_evidence_fields: list[str]
