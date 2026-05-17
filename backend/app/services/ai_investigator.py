from typing import Any


def investigate(evidence: dict[str, Any]) -> dict[str, Any]:
    forwarder = evidence.get("forwarder_status", {})
    splunk = evidence.get("splunk_validation", {})

    findings: list[str] = []
    actions: list[str] = []

    if forwarder:
        findings.append(f"Forwarder workflow status is {forwarder.get('status', 'unknown')}.")
    else:
        findings.append("No forwarder status evidence was provided.")
        actions.append("Run the Splunk Universal Forwarder status check through SSM.")

    if splunk:
        if splunk.get("telemetry_found"):
            findings.append("Splunk telemetry validation found recent matching events.")
        else:
            findings.append("Splunk telemetry validation did not find recent matching events.")
            actions.append("Confirm host/index/sourcetype values and verify forwarder outputs.conf.")
    else:
        findings.append("No Splunk validation evidence was provided.")
        actions.append("Run Splunk ingestion validation after forwarder status is known.")

    if not actions:
        actions.append("Review evidence bundle and hand off validation result to the operating team.")

    return {
        "summary": "Harness generated this investigation from structured workflow evidence only.",
        "findings": findings,
        "recommended_next_actions": actions,
        "cited_evidence_fields": [
            "forwarder_status.status",
            "splunk_validation.telemetry_found",
            "splunk_validation.evidence.sample_count",
        ],
    }
