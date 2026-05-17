from pydantic import BaseModel, Field


class AwsConnectTemplateResponse(BaseModel):
    provider: str = "aws"
    role_name: str
    external_id: str
    template_body: str
    setup_steps: list[str]


class AwsConnectionValidateRequest(BaseModel):
    account_id: str = Field(..., min_length=12, max_length=12)
    role_arn: str = Field(..., min_length=20)
    region: str = Field(..., min_length=5)
    external_id: str = Field(..., min_length=12)
    connection_name: str = "AWS Production"


class AwsRoleStackDeployRequest(BaseModel):
    stack_name: str = Field("harness-operator-access", min_length=1, max_length=128)
    region: str = Field(..., min_length=5)
    trusted_account_id: str = Field(..., min_length=12, max_length=12)
    external_id: str = Field(..., min_length=12)
    approved: bool = False


class CloudConnection(BaseModel):
    connection_id: str
    provider: str
    account_id: str
    region: str
    role_arn: str
    status: str
    created_at: str
    last_validated_at: str | None = None
    validation: dict = Field(default_factory=dict)
