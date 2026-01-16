from fastapi import FastAPI, UploadFile, File, Form, Header, HTTPException, BackgroundTasks, status
import json
from typing import Optional

from .models import (
    InitializeRequest, InitializeResult, ImplementationInfo, Template, ScribeRequest, 
    JobResult, AsyncJobAccepted, SessionCreated, SessionCommitResponse,
    JobStatus
)
from .services import JobManager, SessionManager

app = FastAPI(title="SEP Reference Server", version="1.0.0")

# --- Initialization ---
@app.post("/initialize", response_model=InitializeResult)
def initialize(request: InitializeRequest):
    return InitializeResult(
        protocolVersion="2024-01-01",
        serverInfo=ImplementationInfo(name="SEP Reference Implementation", version="1.0.0"),
        capabilities={
            "logging": {},
            "prompts": {} 
        },
        templates=[
            Template(id="soap_v1", name="SOAP Note", description="Standard SOAP format"),
            Template(id="referral_v1", name="Referral Letter")
        ]
    )

# --- Transcription ---

@app.post("/process", response_model=JobResult)
async def process_sync(
    request: str = Form(..., description="JSON string of ScribeRequest"),
    file: UploadFile = File(...)
):
    try:
        req_dict = json.loads(request)
        req_model = ScribeRequest(**req_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in 'request' field: {str(e)}")

    # For sync, we run processing immediately (blocking)
    job = JobManager.create_job(req_model)
    
    # Simulate processing wait
    await JobManager.run_mock_processing(job.job_id, duration=1)
    
    # Return final result
    final_job = JobManager.get_job(job.job_id)
    return final_job

@app.post("/process/async", response_model=AsyncJobAccepted, status_code=status.HTTP_202_ACCEPTED)
async def process_async(
    background_tasks: BackgroundTasks,
    request: str = Form(...),
    file: UploadFile = File(...)
):
    try:
        req_dict = json.loads(request)
        req_model = ScribeRequest(**req_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

    if not req_model.config or not req_model.config.webhook_url:
        raise HTTPException(status_code=400, detail="Async requests must specify a webhook_url")

    job = JobManager.create_job(req_model)
    
    # Schedule background processing
    background_tasks.add_task(JobManager.run_mock_processing, job.job_id, duration=3)
    
    return AsyncJobAccepted(
        job_id=job.job_id,
        status=JobStatus.QUEUED,
        eta_seconds=3
    )

# --- Session / Chunking ---

@app.post("/session", response_model=SessionCreated, status_code=status.HTTP_201_CREATED)
def create_session(request: ScribeRequest):
    session_id = SessionManager.create_session(request)
    return SessionCreated(session_id=session_id)

@app.post("/session/{session_id}/audio")
async def upload_audio_chunk(
    session_id: str,
    file: UploadFile = File(...),
    x_audio_sequence: int = Header(0)
):
    try:
        chunk_data = await file.read()
        SessionManager.add_chunk(session_id, chunk_data, x_audio_sequence)
        return {"status": "received", "size": len(chunk_data)}
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

@app.post("/session/{session_id}/commit", response_model=SessionCommitResponse, status_code=status.HTTP_202_ACCEPTED)
def commit_session(
    session_id: str,
    background_tasks: BackgroundTasks
):
    try:
        # Commit returns the job, but we need to schedule the processing
        job = SessionManager.commit_session(session_id)
        
        # Schedule the mock processing using FastAPI's BackgroundTasks
        # This replaces the unsafe asyncio.create_task() call inside the service
        background_tasks.add_task(JobManager.run_mock_processing, job.job_id)
        
        return SessionCommitResponse(job_id=job.job_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

# --- Retrieval ---

@app.get("/jobs/{job_id}", response_model=JobResult)
def get_job_status(job_id: str):
    job = JobManager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
