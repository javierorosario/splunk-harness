from typing import Any

from pydantic import BaseModel, Field


class EvidenceGenerateRequest(BaseModel):
    instance: dict[str, Any] = Field(default_factory=dict)
    aws_discovery: dict[str, Any] = Field(default_factory=dict)
    forwarder_check: dict[str, Any] = Field(default_factory=dict)
    ssm_install: dict[str, Any] = Field(default_factory=dict)
    splunk_validation: dict[str, Any] = Field(default_factory=dict)
    ai_summary: dict[str, Any] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    recommended_next_actions: list[str] = Field(default_factory=list)


class EvidenceBundleResponse(BaseModel):
    bundle_id: str
    path: str
    bundle: dict[str, Any]
