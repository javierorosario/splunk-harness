import logging
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from app.config import Settings


logger = logging.getLogger(__name__)


FORWARDER_CHECK_LINUX = """
if command -v /opt/splunkforwarder/bin/splunk >/dev/null 2>&1; then
  /opt/splunkforwarder/bin/splunk status --accept-license
elif command -v splunk >/dev/null 2>&1; then
  splunk status --accept-license
else
  echo "Splunk Universal Forwarder not found"
  exit 3
fi
""".strip()


FORWARDER_INSTALL_PLACEHOLDER_LINUX = """
echo "Harness install workflow placeholder"
echo "Operator approval received; add package download and deployment-server configuration here."
""".strip()


def _session(settings: Settings) -> boto3.Session:
    if settings.aws_profile:
        return boto3.Session(profile_name=settings.aws_profile, region_name=settings.aws_region)
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        return boto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            aws_session_token=settings.aws_session_token or None,
            region_name=settings.aws_region,
        )
    return boto3.Session(region_name=settings.aws_region)


def send_shell_script(settings: Settings, instance_id: str, comment: str, commands: list[str]) -> dict[str, Any]:
    logger.info("Sending SSM command intent='%s' instance_id='%s'", comment, instance_id)
    try:
        ssm = _session(settings).client("ssm")
        response = ssm.send_command(
            InstanceIds=[instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": commands},
            Comment=comment,
            TimeoutSeconds=600,
        )
        command = response["Command"]
        return {
            "command_id": command["CommandId"],
            "status": command.get("Status", "Pending"),
            "comment": comment,
            "instance_id": instance_id,
        }
    except (BotoCoreError, ClientError, NoCredentialsError) as exc:
        raise RuntimeError(f"SSM command failed: {exc}") from exc


def check_forwarder(settings: Settings, instance_id: str) -> dict[str, Any]:
    return send_shell_script(
        settings=settings,
        instance_id=instance_id,
        comment="Harness Splunk Universal Forwarder status check",
        commands=[FORWARDER_CHECK_LINUX],
    )


def install_forwarder_placeholder(settings: Settings, instance_id: str) -> dict[str, Any]:
    return send_shell_script(
        settings=settings,
        instance_id=instance_id,
        comment="Harness operator-approved Splunk Universal Forwarder install/configure workflow",
        commands=[FORWARDER_INSTALL_PLACEHOLDER_LINUX],
    )
