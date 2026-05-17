import re
from typing import Any


SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ASIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(bearer\s+)[a-z0-9._\-+/=]{12,}"),
    re.compile(r"(?i)(splunk\s+)[a-z0-9._\-+/=]{12,}"),
    re.compile(r"(?i)(token|password|secret|session)[\"'\s:=]+[a-z0-9._\-+/=]{8,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.DOTALL),
]


def redact_text(value: str) -> str:
    redacted = value
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: f"{match.group(1)}[REDACTED]" if match.lastindex else "[REDACTED]", redacted)
    return redacted


def redact(value: Any) -> Any:
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, dict):
        cleaned = {}
        for key, item in value.items():
            if any(marker in key.lower() for marker in ("token", "password", "secret", "session", "key")):
                cleaned[key] = "[REDACTED]" if item else item
            else:
                cleaned[key] = redact(item)
        return cleaned
    return value
