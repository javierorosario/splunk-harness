# Harness

Harness is an operational command-center platform for Splunk onboarding, cloud infrastructure discovery, SSH-based host validation, optional cloud-native execution adapters, AI-assisted troubleshooting, and evidence collection.

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
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_SESSION_TOKEN=
SSH_USERNAME=
SSH_PRIVATE_KEY_PATH=
SSH_PORT=22
SSH_CONNECT_TIMEOUT=10
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
- Backend `.env` AWS configuration status check
- EC2 instance discovery
- SSH, manual, and AWS SSM execution adapters
- Splunk Universal Forwarder status check
- Operator-approved install/configure workflow
- Splunk telemetry validation
- AI-assisted evidence summary
- Timestamped local JSON evidence bundle generation

The install/configure endpoint is intentionally a safe placeholder. It verifies operator approval and runs or returns a readable predefined workflow command, but it does not yet download or install Splunk Universal Forwarder packages.

## Platform Adapter Positioning

AWS is the implemented MVP provider path. Azure and Google Cloud are represented with mock discovery adapters to show Harness as a provider-agnostic operational workflow layer. The UI and API keep those mock adapters clearly labeled so demo positioning does not imply unfinished cloud integrations are live.

## Host Execution

Harness separates cloud discovery from host execution. Cloud APIs answer "what infrastructure exists?" while execution adapters answer "what is installed and running on this host?"

Supported execution methods:

- `ssh`: default path for platform-neutral demos. Uses backend `.env` SSH settings and predefined commands only.
- `manual`: returns copy/paste commands for environments where remote execution is not allowed.
- `ssm`: optional AWS-native path when instances are Systems Manager managed nodes.

SSH settings stay in `.env`:

```dotenv
SSH_USERNAME=ec2-user
SSH_PRIVATE_KEY_PATH=/run/secrets/harness_ssh_key
SSH_PORT=22
SSH_CONNECT_TIMEOUT=10
```

Do not put SSH private keys in frontend code. Harness never accepts arbitrary shell commands from the browser.

## AWS Account Connection

For the demo, Harness uses backend `.env` configuration for AWS access. This keeps the operator UI simple and avoids asking users to create IAM roles during a short demo.

### Connect an AWS Account

1. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Configure AWS access in `.env` using one of these options.

   Option A: local AWS profile:

   ```dotenv
   AWS_REGION=us-east-1
   AWS_PROFILE=default
   ```

   Option B: temporary demo credentials:

   ```dotenv
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=...
   AWS_SECRET_ACCESS_KEY=...
   AWS_SESSION_TOKEN=...
   ```

3. Start Harness:

   ```powershell
   docker compose up --build
   ```

4. Open [http://localhost:8000](http://localhost:8000).

5. In **AWS Account Access**, select **Check AWS Config**.

   Harness will call STS from the backend and return a redacted status showing the auth mode, region, and caller identity when credentials are valid.

6. Use the AWS provider tile and select **Discover Instances**.

### Security Notes

- Do not paste AWS access keys into the browser.
- Keep AWS keys and Splunk tokens in `.env` only.
- Harness does not return AWS secrets or STS temporary credentials to frontend code.
- The frontend only displays redacted AWS configuration status.
- For a production system, replace the `.env` demo path with a cross-account IAM role or AWS IAM Identity Center flow.
