from pathlib import Path
from typing import Any

import paramiko

from app.config import Settings
from app.services.ssm_runner import FORWARDER_CHECK_LINUX, FORWARDER_INSTALL_PLACEHOLDER_LINUX


def _resolve_host(host: str | None) -> str:
    if not host:
        raise RuntimeError("SSH execution requires a host or IP address.")
    return host


def _load_private_key(path: str) -> paramiko.PKey:
    if not path:
        raise RuntimeError("SSH_PRIVATE_KEY_PATH is not configured in the backend environment.")
    key_path = Path(path).expanduser()
    if not key_path.exists():
        raise RuntimeError("Configured SSH private key path does not exist.")
    key_errors = []
    for key_type in (paramiko.RSAKey, paramiko.ECDSAKey, paramiko.Ed25519Key):
        try:
            return key_type.from_private_key_file(str(key_path))
        except paramiko.SSHException as exc:
            key_errors.append(str(exc))
    raise RuntimeError(f"Unable to load SSH private key: {'; '.join(key_errors)}")


def run_ssh_command(
    settings: Settings,
    host: str | None,
    command: str,
    username: str | None = None,
    port: int | None = None,
) -> dict[str, Any]:
    resolved_host = _resolve_host(host)
    resolved_username = username or settings.ssh_username
    resolved_port = port or settings.ssh_port
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=resolved_host,
            port=resolved_port,
            username=resolved_username,
            pkey=_load_private_key(settings.ssh_private_key_path),
            timeout=settings.ssh_connect_timeout,
            banner_timeout=settings.ssh_connect_timeout,
            auth_timeout=settings.ssh_connect_timeout,
        )
        stdin, stdout, stderr = client.exec_command(command, timeout=120)
        exit_code = stdout.channel.recv_exit_status()
        return {
            "execution_method": "ssh",
            "status": "succeeded" if exit_code == 0 else "failed",
            "host": resolved_host,
            "username": resolved_username,
            "port": resolved_port,
            "exit_code": exit_code,
            "stdout": stdout.read().decode("utf-8", errors="replace"),
            "stderr": stderr.read().decode("utf-8", errors="replace"),
        }
    except Exception as exc:
        return {
            "execution_method": "ssh",
            "status": "failed",
            "host": resolved_host,
            "username": resolved_username,
            "port": resolved_port,
            "error": str(exc),
        }
    finally:
        client.close()


def check_forwarder_ssh(settings: Settings, host: str | None, username: str | None = None, port: int | None = None) -> dict:
    return run_ssh_command(settings, host, FORWARDER_CHECK_LINUX, username=username, port=port)


def install_forwarder_ssh(settings: Settings, host: str | None, username: str | None = None, port: int | None = None) -> dict:
    return run_ssh_command(settings, host, FORWARDER_INSTALL_PLACEHOLDER_LINUX, username=username, port=port)
