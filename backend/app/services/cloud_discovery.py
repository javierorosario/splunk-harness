from app.config import Settings
from app.services.aws_discovery import discover_instances


MOCK_PROVIDER_RESOURCES = {
    "azure": [
        {
            "instance_id": "azure-vm-demo-01",
            "name": "payments-api-vm",
            "state": "running",
            "private_ip": "10.42.8.14",
            "public_ip": None,
            "platform": "linux",
            "provider": "azure",
            "provider_resource_type": "virtual_machine",
            "ssm_managed": True,
            "management_channel": "azure_run_command",
        },
        {
            "instance_id": "azure-vm-demo-02",
            "name": "batch-worker-vm",
            "state": "stopped",
            "private_ip": "10.42.9.22",
            "public_ip": None,
            "platform": "windows",
            "provider": "azure",
            "provider_resource_type": "virtual_machine",
            "ssm_managed": False,
            "management_channel": "azure_run_command",
        },
    ],
    "gcp": [
        {
            "instance_id": "gcp-vm-demo-01",
            "name": "checkout-service-vm",
            "state": "RUNNING",
            "private_ip": "10.128.0.12",
            "public_ip": "34.75.120.10",
            "platform": "debian-12",
            "provider": "gcp",
            "provider_resource_type": "compute_instance",
            "ssm_managed": True,
            "management_channel": "os_config",
        },
        {
            "instance_id": "gcp-vm-demo-02",
            "name": "reporting-vm",
            "state": "TERMINATED",
            "private_ip": "10.128.0.19",
            "public_ip": None,
            "platform": "ubuntu-2204",
            "provider": "gcp",
            "provider_resource_type": "compute_instance",
            "ssm_managed": False,
            "management_channel": "os_config",
        },
    ],
}


def discover_provider_resources(settings: Settings, provider: str) -> dict:
    normalized = provider.lower()
    if normalized == "aws":
        instances = discover_instances(settings)
        return {
            "instances": instances,
            "count": len(instances),
            "source": "aws",
            "provider": "aws",
            "mocked": False,
        }

    if normalized in MOCK_PROVIDER_RESOURCES:
        resources = MOCK_PROVIDER_RESOURCES[normalized]
        return {
            "instances": resources,
            "count": len(resources),
            "source": f"{normalized}_mock_adapter",
            "provider": normalized,
            "mocked": True,
        }

    raise ValueError(f"Unsupported provider '{provider}'")
