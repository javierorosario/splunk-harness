from pydantic import BaseModel


class SplunkValidationRequest(BaseModel):
    instance_id: str
    hostname: str | None = None
    index: str | None = None
    sourcetype: str | None = None


class SplunkValidationResult(BaseModel):
    status: str
    telemetry_found: bool
    query: str
    evidence: dict
