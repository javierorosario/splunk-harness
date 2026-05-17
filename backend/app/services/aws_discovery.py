import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from app.config import Settings


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


def _name_tag(tags: list[dict] | None) -> str | None:
    for tag in tags or []:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return None


def _platform(instance: dict) -> str:
    if instance.get("Platform"):
        return instance["Platform"]
    details = instance.get("PlatformDetails")
    return details or "linux/unix"


def discover_instances(settings: Settings) -> list[dict]:
    try:
        session = _session(settings)
        ec2 = session.client("ec2")
        ssm = session.client("ssm")

        paginator = ec2.get_paginator("describe_instances")
        instances: list[dict] = []
        instance_ids: list[str] = []

        for page in paginator.paginate():
            for reservation in page.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    instance_id = instance["InstanceId"]
                    instance_ids.append(instance_id)
                    instances.append(
                        {
                            "instance_id": instance_id,
                            "name": _name_tag(instance.get("Tags")),
                            "state": instance.get("State", {}).get("Name", "unknown"),
                            "private_ip": instance.get("PrivateIpAddress"),
                            "public_ip": instance.get("PublicIpAddress"),
                            "platform": _platform(instance),
                            "ssm_managed": False,
                        }
                    )

        if instance_ids:
            managed_ids = set()
            for start in range(0, len(instance_ids), 50):
                chunk = instance_ids[start : start + 50]
                response = ssm.describe_instance_information(
                    Filters=[{"Key": "InstanceIds", "Values": chunk}]
                )
                managed_ids.update(item["InstanceId"] for item in response.get("InstanceInformationList", []))

            for instance in instances:
                instance["ssm_managed"] = instance["instance_id"] in managed_ids

        return instances
    except (BotoCoreError, ClientError, NoCredentialsError) as exc:
        raise RuntimeError(f"AWS discovery failed: {exc}") from exc
