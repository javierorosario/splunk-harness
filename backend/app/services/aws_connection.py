import textwrap
from datetime import UTC, datetime
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from app.services.connection_store import save_connection


ROLE_NAME = "HarnessOperatorAccess"


def generate_external_id() -> str:
    return f"harness-{uuid4().hex}"


def build_cloudformation_template(external_id: str) -> str:
    return textwrap.dedent(
        f"""
        AWSTemplateFormatVersion: '2010-09-09'
        Description: Harness cross-account role for operator-approved observability onboarding workflows.
        Parameters:
          HarnessTrustedAccountId:
            Type: String
            Description: AWS account ID where Harness is running.
        Resources:
          HarnessOperatorAccessRole:
            Type: AWS::IAM::Role
            Properties:
              RoleName: {ROLE_NAME}
              AssumeRolePolicyDocument:
                Version: '2012-10-17'
                Statement:
                  - Effect: Allow
                    Principal:
                      AWS: !Sub arn:aws:iam::${{HarnessTrustedAccountId}}:root
                    Action: sts:AssumeRole
                    Condition:
                      StringEquals:
                        sts:ExternalId: {external_id}
              Policies:
                - PolicyName: HarnessMvpOperations
                  PolicyDocument:
                    Version: '2012-10-17'
                    Statement:
                      - Sid: DiscoveryReadOnly
                        Effect: Allow
                        Action:
                          - ec2:DescribeInstances
                          - ec2:DescribeTags
                          - ssm:DescribeInstanceInformation
                        Resource: '*'
                      - Sid: OperatorApprovedSsm
                        Effect: Allow
                        Action:
                          - ssm:SendCommand
                          - ssm:GetCommandInvocation
                          - ssm:ListCommandInvocations
                        Resource: '*'
        Outputs:
          HarnessRoleArn:
            Description: Role ARN to paste into Harness.
            Value: !GetAtt HarnessOperatorAccessRole.Arn
        """
    ).strip()


def connect_template() -> dict:
    external_id = generate_external_id()
    return {
        "provider": "aws",
        "role_name": ROLE_NAME,
        "external_id": external_id,
        "template_body": build_cloudformation_template(external_id),
        "setup_steps": [
            "Copy the CloudFormation template into the AWS account you want Harness to inspect.",
            "Set HarnessTrustedAccountId to the AWS account ID where Harness credentials run.",
            "Create the stack and copy the HarnessRoleArn output.",
            "Paste the role ARN, account ID, region, and external ID into Harness validation.",
        ],
    }


def deploy_role_stack(
    stack_name: str,
    region: str,
    trusted_account_id: str,
    external_id: str,
) -> dict:
    try:
        cloudformation = boto3.client("cloudformation", region_name=region)
        response = cloudformation.create_stack(
            StackName=stack_name,
            TemplateBody=build_cloudformation_template(external_id),
            Parameters=[
                {
                    "ParameterKey": "HarnessTrustedAccountId",
                    "ParameterValue": trusted_account_id,
                }
            ],
            Capabilities=["CAPABILITY_NAMED_IAM"],
            Tags=[
                {"Key": "Application", "Value": "Harness"},
                {"Key": "Purpose", "Value": "ObservabilityOnboarding"},
            ],
        )
        return {
            "status": "create_initiated",
            "stack_id": response.get("StackId"),
            "stack_name": stack_name,
            "region": region,
            "role_name": ROLE_NAME,
            "template_delivery": "TemplateBody",
            "requires_s3_template": False,
            "next_step": "Wait for CREATE_COMPLETE, then copy the HarnessRoleArn stack output into Harness validation.",
        }
    except (BotoCoreError, ClientError, NoCredentialsError) as exc:
        return {
            "status": "create_failed",
            "stack_name": stack_name,
            "region": region,
            "role_name": ROLE_NAME,
            "template_delivery": "TemplateBody",
            "requires_s3_template": False,
            "error": str(exc),
        }


def validate_connection(account_id: str, role_arn: str, region: str, external_id: str, connection_name: str) -> dict:
    checks = []
    missing_permissions = []
    now = datetime.now(UTC).isoformat()

    try:
        sts = boto3.client("sts", region_name=region)
        assumed = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName="HarnessValidation",
            ExternalId=external_id,
            DurationSeconds=900,
        )
        credentials = assumed["Credentials"]
        session = boto3.Session(
            aws_access_key_id=credentials["AccessKeyId"],
            aws_secret_access_key=credentials["SecretAccessKey"],
            aws_session_token=credentials["SessionToken"],
            region_name=region,
        )

        identity = session.client("sts").get_caller_identity()
        checks.append({"name": "sts:GetCallerIdentity", "status": "ok", "account": identity.get("Account")})

        try:
            session.client("ec2").describe_instances(MaxResults=5)
            checks.append({"name": "ec2:DescribeInstances", "status": "ok"})
        except ClientError as exc:
            missing_permissions.append("ec2:DescribeInstances")
            checks.append({"name": "ec2:DescribeInstances", "status": "failed", "detail": str(exc)})

        try:
            session.client("ssm").describe_instance_information(MaxResults=5)
            checks.append({"name": "ssm:DescribeInstanceInformation", "status": "ok"})
        except ClientError as exc:
            missing_permissions.append("ssm:DescribeInstanceInformation")
            checks.append({"name": "ssm:DescribeInstanceInformation", "status": "failed", "detail": str(exc)})

        status = "connected" if not missing_permissions else "permission_issue"
        record = save_connection(
            {
                "provider": "aws",
                "account_id": account_id,
                "region": region,
                "role_arn": role_arn,
                "status": status,
                "connection_name": connection_name,
                "last_validated_at": now,
                "validation": {"checks": checks, "missing_permissions": missing_permissions},
            }
        )
        return record
    except (BotoCoreError, ClientError, NoCredentialsError) as exc:
        record = save_connection(
            {
                "provider": "aws",
                "account_id": account_id,
                "region": region,
                "role_arn": role_arn,
                "status": "validation_failed",
                "connection_name": connection_name,
                "last_validated_at": now,
                "validation": {"checks": checks, "missing_permissions": missing_permissions, "error": str(exc)},
            }
        )
        return record
