from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

# Import the new service
from kubernetes.service import InvestigationService

app = FastAPI(title="AI Kubernetes Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up AI Kubernetes Troubleshooting Agent Backend...")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-kubernetes-agent"}

# --- NEW ENDPOINT ---
@app.post("/investigate")
async def investigate_cluster():
    evidence = InvestigationService.run_full_investigation()
    return {
        "status": "success",
        "investigation": evidence
    }