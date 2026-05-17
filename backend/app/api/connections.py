from fastapi import APIRouter, HTTPException
import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from app.config import get_settings
from app.schemas.connections import AwsConnectionValidateRequest, AwsConnectTemplateResponse, AwsRoleStackDeployRequest
from app.services.aws_connection import connect_template, deploy_role_stack, validate_connection
from app.services.connection_store import list_connections
from app.utils.redaction import redact


router = APIRouter(prefix="/api/cloud", tags=["connections"])


@router.get("/aws/connect-template", response_model=AwsConnectTemplateResponse)
def aws_connect_template() -> dict:
    return redact(connect_template())


@router.post("/aws/connect-stack")
def aws_connect_stack(request: AwsRoleStackDeployRequest) -> dict:
    if not request.approved:
        raise HTTPException(status_code=400, detail="Operator approval is required before creating IAM resources.")

    result = deploy_role_stack(
        stack_name=request.stack_name,
        region=request.region,
        trusted_account_id=request.trusted_account_id,
        external_id=request.external_id,
    )
    return redact(result)


@router.post("/aws/connections/validate")
def aws_validate_connection(request: AwsConnectionValidateRequest) -> dict:
    result = validate_connection(
        account_id=request.account_id,
        role_arn=request.role_arn,
        region=request.region,
        external_id=request.external_id,
        connection_name=request.connection_name,
    )
    return redact(result)


@router.get("/connections")
def connections() -> dict:
    return {"connections": redact(list_connections())}


@router.get("/aws/config-status")
def aws_config_status() -> dict:
    settings = get_settings()
    status = {
        "provider": "aws",
        "configured": settings.aws_configured,
        "region": settings.aws_region,
        "auth_mode": settings.aws_auth_mode,
        "profile": settings.aws_profile or None,
        "has_access_key": bool(settings.aws_access_key_id),
        "has_session_token": bool(settings.aws_session_token),
        "identity": None,
        "status": "not_checked",
    }
    try:
        if settings.aws_profile:
            session = boto3.Session(profile_name=settings.aws_profile, region_name=settings.aws_region)
        elif settings.aws_access_key_id and settings.aws_secret_access_key:
            session = boto3.Session(
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                aws_session_token=settings.aws_session_token or None,
                region_name=settings.aws_region,
            )
        else:
            session = boto3.Session(region_name=settings.aws_region)

        identity = session.client("sts").get_caller_identity()
        status["identity"] = {
            "account": identity.get("Account"),
            "arn": identity.get("Arn"),
            "user_id": identity.get("UserId"),
        }
        status["status"] = "connected"
    except (BotoCoreError, ClientError, NoCredentialsError) as exc:
        status["status"] = "not_connected"
        status["detail"] = str(exc)
    return redact(status)
