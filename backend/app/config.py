from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()

if os.getenv("AWS_PROFILE", "") == "":
    os.environ.pop("AWS_PROFILE", None)
if os.getenv("AWS_DEFAULT_PROFILE", "") == "":
    os.environ.pop("AWS_DEFAULT_PROFILE", None)


class Settings(BaseModel):
    app_name: str = "Harness"
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_profile: str = os.getenv("AWS_PROFILE", "")
    aws_access_key_id: str = os.getenv("AWS_ACCESS_KEY_ID", "")
    aws_secret_access_key: str = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_session_token: str = os.getenv("AWS_SESSION_TOKEN", "")
    ssh_username: str = os.getenv("SSH_USERNAME", "ec2-user")
    ssh_private_key_path: str = os.getenv("SSH_PRIVATE_KEY_PATH", "")
    ssh_port: int = int(os.getenv("SSH_PORT", "22"))
    ssh_connect_timeout: int = int(os.getenv("SSH_CONNECT_TIMEOUT", "10"))
    splunk_base_url: str = os.getenv("SPLUNK_BASE_URL", "")
    splunk_token: str = os.getenv("SPLUNK_TOKEN", "")
    splunk_verify_ssl: bool = os.getenv("SPLUNK_VERIFY_SSL", "true").lower() == "true"
    splunk_default_index: str = os.getenv("SPLUNK_DEFAULT_INDEX", "main")
    ai_provider: str = os.getenv("AI_PROVIDER", "local")
    ai_api_key: str = os.getenv("AI_API_KEY", "")

    @property
    def aws_configured(self) -> bool:
        return bool(self.aws_region and (self.aws_profile or self.aws_access_key_id or os.getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI") or os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE") or os.getenv("AWS_EC2_METADATA_DISABLED") != "true"))

    @property
    def aws_auth_mode(self) -> str:
        if self.aws_profile:
            return "profile"
        if self.aws_access_key_id:
            return "environment_keys"
        if os.getenv("AWS_WEB_IDENTITY_TOKEN_FILE"):
            return "web_identity"
        if os.getenv("AWS_CONTAINER_CREDENTIALS_RELATIVE_URI"):
            return "container_credentials"
        return "default_provider_chain"

    @property
    def splunk_configured(self) -> bool:
        return bool(self.splunk_base_url and self.splunk_token)

    @property
    def ai_configured(self) -> bool:
        return self.ai_provider == "local" or bool(self.ai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
