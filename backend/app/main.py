from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import ai, aws, cloud, connections, evidence, health, splunk, workflows
from app.utils.logging import configure_logging


configure_logging()

app = FastAPI(
    title="Harness",
    description="Operational command center for Splunk onboarding and evidence-backed validation.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(aws.router)
app.include_router(cloud.router)
app.include_router(connections.router)
app.include_router(workflows.router)
app.include_router(splunk.router)
app.include_router(ai.router)
app.include_router(evidence.router)

frontend_dir = Path(__file__).resolve().parents[1] / "frontend"
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
