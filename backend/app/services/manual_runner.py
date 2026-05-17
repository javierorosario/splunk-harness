from app.services.ssm_runner import FORWARDER_CHECK_LINUX, FORWARDER_INSTALL_PLACEHOLDER_LINUX


def manual_forwarder_check(instance_id: str, host: str | None) -> dict:
    return {
        "execution_method": "manual",
        "status": "manual_action_required",
        "instance_id": instance_id,
        "host": host,
        "commands": [FORWARDER_CHECK_LINUX],
        "detail": "Run the generated command on the host and paste the result into operational notes.",
    }


def manual_forwarder_install(instance_id: str, host: str | None) -> dict:
    return {
        "execution_method": "manual",
        "status": "manual_action_required",
        "instance_id": instance_id,
        "host": host,
        "commands": [FORWARDER_INSTALL_PLACEHOLDER_LINUX],
        "detail": "Run the generated install/configure command on the host after operator approval.",
    }
