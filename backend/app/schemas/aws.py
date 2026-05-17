from pydantic import BaseModel


class Ec2Instance(BaseModel):
    instance_id: str
    name: str | None = None
    state: str
    private_ip: str | None = None
    public_ip: str | None = None
    platform: str
    provider: str = "aws"
    provider_resource_type: str = "ec2_instance"
    ssm_managed: bool = False
    management_channel: str = "ssm"


class InstanceListResponse(BaseModel):
    instances: list[Ec2Instance]
    count: int
    source: str = "aws"
    provider: str = "aws"
    mocked: bool = False
