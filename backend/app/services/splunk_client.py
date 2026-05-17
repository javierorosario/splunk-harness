from typing import Any

import requests

from app.config import Settings


class SplunkClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.splunk_base_url.rstrip("/")
        self.token = settings.splunk_token
        self.verify_ssl = settings.splunk_verify_ssl

    def search_oneshot(self, query: str) -> dict[str, Any]:
        if not self.base_url or not self.token:
            raise RuntimeError("Splunk is not configured")

        response = requests.post(
            f"{self.base_url}/services/search/jobs/oneshot",
            headers={"Authorization": f"Bearer {self.token}"},
            data={"search": query, "output_mode": "json", "count": "5"},
            timeout=30,
            verify=self.verify_ssl,
        )
        response.raise_for_status()
        return response.json()
