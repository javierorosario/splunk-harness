const backendStatus = document.querySelector("#backend-status");
const refreshButton = document.querySelector("#refresh-health");
const healthGrid = document.querySelector("#health-grid");
const healthEvidence = document.querySelector("#health-evidence");
const providerNote = document.querySelector("#provider-note");
const discoveryCopy = document.querySelector("#discovery-copy");
const discoverButton = document.querySelector("#discover-instances");
const instancesTable = document.querySelector("#instances-table");
const instanceIdInput = document.querySelector("#instance-id");
const selectedInstance = document.querySelector("#selected-instance");
const executionMethod = document.querySelector("#execution-method");
const sshHostInput = document.querySelector("#ssh-host");
const awsAccessStatus = document.querySelector("#aws-access-status");
const awsAccessDetail = document.querySelector("#aws-access-detail");
const forwarderResult = document.querySelector("#forwarder-result");
const installApproved = document.querySelector("#install-approved");
const installResult = document.querySelector("#install-result");
const splunkResult = document.querySelector("#splunk-result");
const aiResult = document.querySelector("#ai-result");
const evidenceResult = document.querySelector("#evidence-result");

let selectedInstanceData = {};
let lastForwarderResult = {};
let lastInstallResult = {};
let lastSplunkResult = {};
let lastAiResult = {};
let selectedProvider = "aws";

const providerDetails = {
  aws: {
    note: "AWS is the implemented demo path. Azure and Google Cloud are shown as platform adapter targets for the same onboarding and evidence workflow.",
    discovery: "List EC2 metadata, state, IPs, platform, and SSM managed status.",
    action: "Discover Instances",
    enabled: true,
  },
  azure: {
    note: "Azure is mocked in this MVP to show the adapter model. The same workflow would target VM inventory, Run Command, Splunk validation, and evidence bundles.",
    discovery: "Mock target: list Azure VM metadata, power state, private IPs, OS type, and Run Command readiness.",
    action: "Mock Azure Discovery",
    enabled: true,
  },
  gcp: {
    note: "Google Cloud is mocked in this MVP to show the adapter model. The same workflow would target Compute Engine, OS Config, Splunk validation, and evidence bundles.",
    discovery: "Mock target: list Compute Engine metadata, status, network IPs, OS image, and OS Config readiness.",
    action: "Mock GCP Discovery",
    enabled: true,
  },
};

function badge(text, state) {
  backendStatus.textContent = text;
  backendStatus.className = `badge badge-${state}`;
}

function renderHealth(data) {
  const items = [
    ["Backend", data.status === "ok" ? "Online" : "Unknown"],
    ["AWS", data.aws_configured ? "Configured" : "Missing config"],
    ["Splunk", data.splunk_configured ? "Configured" : "Missing config"],
    ["AI Provider", data.ai_provider || "Not set"],
  ];

  healthGrid.innerHTML = items
    .map(([label, value]) => `
      <div class="status-item">
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `)
    .join("");

  healthEvidence.textContent = JSON.stringify(data, null, 2);
}

async function checkHealth() {
  refreshButton.disabled = true;
  badge("Checking backend", "waiting");

  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error(`Backend returned HTTP ${response.status}`);
    }

    const data = await response.json();
    renderHealth(data);
    badge("Backend online", "ok");
  } catch (error) {
    badge("Backend offline", "bad");
    healthEvidence.textContent = error.message;
  } finally {
    refreshButton.disabled = false;
  }
}

refreshButton.addEventListener("click", checkHealth);
checkHealth();

document.querySelectorAll(".provider-tile").forEach((tile) => {
  tile.addEventListener("click", () => {
    const provider = tile.dataset.provider;
    const details = providerDetails[provider];
    selectedProvider = provider;
    selectedInstanceData = {};
    instanceIdInput.value = "";
    selectedInstance.textContent = "No instance selected.";

    document.querySelectorAll(".provider-tile").forEach((item) => {
      item.classList.toggle("active-provider", item === tile);
    });

    providerNote.textContent = details.note;
    discoveryCopy.textContent = details.discovery;
    discoverButton.textContent = details.action;
    discoverButton.disabled = !details.enabled;
    instancesTable.textContent = details.enabled
      ? ""
      : "This provider adapter is planned for a later implementation.";
  });
});

document.querySelector("#refresh-aws-config").addEventListener("click", async () => {
  awsAccessStatus.textContent = "Checking";
  awsAccessStatus.className = "badge badge-waiting";
  awsAccessDetail.textContent = "Checking backend AWS credentials...";
  try {
    const response = await fetch("/api/cloud/aws/config-status");
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }
    if (data.status === "connected") {
      awsAccessStatus.textContent = "Connected";
      awsAccessStatus.className = "badge badge-ok";
      awsAccessDetail.textContent = `${data.auth_mode} in ${data.region} (${data.identity?.account || "account available"})`;
    } else {
      awsAccessStatus.textContent = "Unavailable";
      awsAccessStatus.className = "badge badge-bad";
      awsAccessDetail.textContent = data.detail || "AWS credentials are not available to the backend.";
    }
  } catch (error) {
    awsAccessStatus.textContent = "Unavailable";
    awsAccessStatus.className = "badge badge-bad";
    awsAccessDetail.textContent = error.message;
  }
});

function getInstanceId() {
  return instanceIdInput.value.trim();
}

function writeJson(element, value) {
  element.textContent = JSON.stringify(value, null, 2);
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || `HTTP ${response.status}`);
  }
  return data;
}

discoverButton.addEventListener("click", async () => {
  discoverButton.disabled = true;
  instancesTable.textContent = `Discovering ${selectedProvider.toUpperCase()} resources...`;
  try {
    const response = await fetch(`/api/cloud/${selectedProvider}/resources`);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || `HTTP ${response.status}`);
    }

    instancesTable.innerHTML = `
      <table>
        <thead>
          <tr><th>ID</th><th>Name</th><th>State</th><th>Private IP</th><th>SSM</th></tr>
        </thead>
        <tbody></tbody>
      </table>
    `;

    const tbody = instancesTable.querySelector("tbody");
    data.instances.forEach((instance) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${escapeHtml(instance.instance_id)}</td>
        <td>${escapeHtml(instance.name)}</td>
        <td>${escapeHtml(instance.state)}</td>
        <td>${escapeHtml(instance.private_ip)}</td>
        <td>${escapeHtml(instance.management_channel)} ${instance.ssm_managed ? "ready" : "not ready"}</td>
      `;
      row.addEventListener("click", () => {
        selectedInstanceData = instance;
        instanceIdInput.value = selectedInstanceData.instance_id;
        sshHostInput.value = selectedInstanceData.private_ip || selectedInstanceData.public_ip || "";
        writeJson(selectedInstance, selectedInstanceData);
      });
      tbody.appendChild(row);
    });
    if (data.mocked) {
      const note = document.createElement("p");
      note.className = "mock-note";
      note.textContent = "Mock adapter data for demo positioning. The workflow shape is shared; provider execution is not implemented yet.";
      instancesTable.prepend(note);
    }
  } catch (error) {
    instancesTable.textContent = error.message;
  } finally {
    discoverButton.disabled = false;
  }
});

document.querySelector("#check-forwarder").addEventListener("click", async () => {
  forwarderResult.textContent = `Running ${executionMethod.value.toUpperCase()} forwarder check...`;
  try {
    lastForwarderResult = await postJson("/api/workflows/check-forwarder", {
      instance_id: getInstanceId(),
      execution_method: executionMethod.value,
      host: sshHostInput.value.trim() || selectedInstanceData.private_ip || selectedInstanceData.public_ip || null,
    });
    writeJson(forwarderResult, lastForwarderResult);
  } catch (error) {
    forwarderResult.textContent = error.message;
  }
});

document.querySelector("#install-forwarder").addEventListener("click", async () => {
  installResult.textContent = "Starting approved install workflow...";
  try {
    lastInstallResult = await postJson("/api/workflows/install-forwarder", {
      instance_id: getInstanceId(),
      execution_method: executionMethod.value,
      host: sshHostInput.value.trim() || selectedInstanceData.private_ip || selectedInstanceData.public_ip || null,
      options: { approved: installApproved.checked },
    });
    writeJson(installResult, lastInstallResult);
  } catch (error) {
    installResult.textContent = error.message;
  }
});

document.querySelector("#validate-splunk").addEventListener("click", async () => {
  splunkResult.textContent = "Validating Splunk ingestion...";
  try {
    lastSplunkResult = await postJson("/api/splunk/validate-ingestion", {
      instance_id: getInstanceId(),
      hostname: document.querySelector("#hostname").value.trim() || null,
      index: document.querySelector("#splunk-index").value.trim() || null,
      sourcetype: document.querySelector("#sourcetype").value.trim() || null,
    });
    writeJson(splunkResult, lastSplunkResult);
  } catch (error) {
    splunkResult.textContent = error.message;
  }
});

document.querySelector("#run-investigation").addEventListener("click", async () => {
  aiResult.textContent = "Generating evidence-grounded summary...";
  try {
    lastAiResult = await postJson("/api/ai/investigate", {
      instance: selectedInstanceData,
      forwarder_status: lastForwarderResult,
      splunk_validation: lastSplunkResult,
      evidence_context: { ssm_install: lastInstallResult },
    });
    writeJson(aiResult, lastAiResult);
  } catch (error) {
    aiResult.textContent = error.message;
  }
});

document.querySelector("#generate-evidence").addEventListener("click", async () => {
  evidenceResult.textContent = "Writing evidence bundle...";
  try {
    const result = await postJson("/api/evidence/generate", {
      instance: selectedInstanceData,
      aws_discovery: { provider: selectedProvider, mocked: selectedProvider !== "aws" },
      forwarder_check: lastForwarderResult,
      ssm_install: lastInstallResult,
      splunk_validation: lastSplunkResult,
      ai_summary: lastAiResult,
      findings: lastAiResult.findings || [],
      recommended_next_actions: lastAiResult.recommended_next_actions || [],
    });
    writeJson(evidenceResult, result);
  } catch (error) {
    evidenceResult.textContent = error.message;
  }
});
