# Harness

Harness is an operational command-center platform for Splunk onboarding, AWS infrastructure discovery, SSM-based validation workflows, AI-assisted troubleshooting, and evidence collection.

The MVP intentionally uses a low-dependency stack:

- Backend: Python FastAPI
- Frontend: static HTML, CSS, and vanilla JavaScript
- Runtime: Docker Compose
- AWS integration: boto3
- Splunk integration: Splunk REST API and HEC-oriented validation
- Evidence storage: timestamped local JSON files under `backend/app/storage/evidence/`

## Local Setup

This project is designed to run through Docker. Local Python is not required.

1. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Edit `.env` with local AWS and Splunk settings.

3. Build and start Harness:

   ```powershell
   docker compose up --build
   ```

4. Open the operator UI:

   [http://localhost:8000](http://localhost:8000)

5. Check the backend directly:

   [http://localhost:8000/api/health](http://localhost:8000/api/health)

## Configuration

Secrets must stay in `.env` or the runtime environment. Do not put AWS credentials, Splunk tokens, or AI provider keys in frontend files.

Required configuration keys:

```dotenv
AWS_REGION=
AWS_PROFILE=
SPLUNK_BASE_URL=
SPLUNK_TOKEN=
SPLUNK_VERIFY_SSL=true
SPLUNK_DEFAULT_INDEX=
AI_PROVIDER=
AI_API_KEY=
```

## Current MVP Status

Implemented:

- Docker Compose boot path
- FastAPI application
- `/api/health`
- Static frontend served by FastAPI
- Frontend backend-connectivity check
- Environment template
- Basic redaction utility foundation
- Provider-aware discovery API with AWS live adapter and Azure/GCP mock adapters
- EC2 instance discovery
- SSM command runner abstraction
- Splunk Universal Forwarder status check
- Operator-approved SSM install/configure workflow
- Splunk telemetry validation
- AI-assisted evidence summary
- Timestamped local JSON evidence bundle generation

The SSM install/configure endpoint is intentionally a safe placeholder. It verifies operator approval and sends a readable predefined SSM command, but it does not yet download or install Splunk Universal Forwarder packages.

## Platform Adapter Positioning

AWS is the implemented MVP provider path. Azure and Google Cloud are represented with mock discovery adapters to show Harness as a provider-agnostic operational workflow layer. The UI and API keep those mock adapters clearly labeled so demo positioning does not imply unfinished cloud integrations are live.
