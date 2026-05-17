from typing import Any

from pydantic import BaseModel, Field


class InstanceRequest(BaseModel):
    instance_id: str = Field(..., min_length=3)


class ForwarderInstallOptions(BaseModel):
    splunk_deployment_server: str | None = None
    splunk_index: str | None = None
    splunk_hec_url: str | None = None
    approved: bool = False


class ForwarderInstallRequest(InstanceRequest):
    options: ForwarderInstallOptions


class WorkflowResult(BaseModel):
    instance_id: str
    status: str
    detail: str
    evidence: dict[str, Any] = Field(default_factory=dict)
