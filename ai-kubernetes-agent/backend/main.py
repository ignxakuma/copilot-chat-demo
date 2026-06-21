import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

from kubernetes.service import InvestigationService
from ai.reasoning_engine import RootCauseAnalyzer

app = FastAPI(title="AI Kubernetes Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Define the Expected Payload
class InvestigateRequest(BaseModel):
    namespace: str = "default"

# In-memory database for tracking history
investigation_history = [
    {
        "timestamp": "2026-06-21 08:32:15",
        "root_cause": "OOMKilled - Container exceeded memory limits.",
        "namespace": "default",
        "confidence": 98,
        "status": "success"
    },
    {
        "timestamp": "2026-06-21 08:14:02",
        "root_cause": "CrashLoopBackOff - Missing DATABASE_URL environment variable.",
        "namespace": "production",
        "confidence": 92,
        "status": "success"
    }
]

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-kubernetes-agent"}

# --- NEW ENDPOINT: GET HISTORY ---
@app.get("/history")
async def get_history():
    return {"status": "success", "history": investigation_history}

@app.post("/investigate")
async def investigate_cluster(request: InvestigateRequest):
    # Pass the namespace to the investigation service
    logger.info(f"Phase 1: Gathering cluster evidence for namespace: {request.namespace}...")
    evidence = InvestigationService.run_full_investigation(namespace=request.namespace)
    
    logger.info("Phase 2: Generating AI diagnosis...")
    diagnosis = await RootCauseAnalyzer.analyze(evidence)
    
    record = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "pod_name": diagnosis.get("pod_name", "Unknown"),
        "container_name": diagnosis.get("container_name", "Unknown"),
        "root_cause": diagnosis.get("root_cause", "Unknown Incident"),
        "confidence": diagnosis.get("confidence", 0),
        # 3. Use the dynamic namespace for the history record
        "namespace": request.namespace, 
        "status": "success" if diagnosis.get("confidence", 0) > 0 else "failed"
    }
    investigation_history.insert(0, record) 
    
    return {
        "status": "success",
        "diagnosis": diagnosis
    }