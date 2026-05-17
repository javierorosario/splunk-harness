from functools import lru_cache
import os

from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()


class Settings(BaseModel):
    app_name: str = "Harness"
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    aws_profile: str = os.getenv("AWS_PROFILE", "")
    splunk_base_url: str = os.getenv("SPLUNK_BASE_URL", "")
    splunk_token: str = os.getenv("SPLUNK_TOKEN", "")
    splunk_verify_ssl: bool = os.getenv("SPLUNK_VERIFY_SSL", "true").lower() == "true"
    splunk_default_index: str = os.getenv("SPLUNK_DEFAULT_INDEX", "main")
    ai_provider: str = os.getenv("AI_PROVIDER", "local")
    ai_api_key: str = os.getenv("AI_API_KEY", "")

    @property
    def aws_configured(self) -> bool:
        return bool(self.aws_region)

    @property
    def splunk_configured(self) -> bool:
        return bool(self.splunk_base_url and self.splunk_token)

    @property
    def ai_configured(self) -> bool:
        return self.ai_provider == "local" or bool(self.ai_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
