import uuid
import datetime
import asyncio
from typing import Dict, List, Optional
from .models import JobResult, JobStatus, ScribeOutput, ScribeRequest

# In-memory storage for reference implementation
JOBS: Dict[str, JobResult] = {}
JOB_REQUESTS: Dict[str, ScribeRequest] = {}
SESSIONS: Dict[str, Dict] = {}

class JobManager:
    @staticmethod
    def create_job(req: ScribeRequest) -> JobResult:
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        now = datetime.datetime.now(datetime.UTC).isoformat()
        
        job = JobResult(
            job_id=job_id,
            status=JobStatus.QUEUED,
            created_at=now
        )
        # Store request separately to access templates later
        JOB_REQUESTS[job_id] = req
        JOBS[job_id] = job
        return job

    @staticmethod
    async def run_mock_processing(job_id: str, duration: int = 2):
        """Simulates processing delay and updates job to completed."""
        job = JOBS.get(job_id)
        if not job:
            return
            
        job.status = JobStatus.PROCESSING
        await asyncio.sleep(duration)
        
        # Mock Output based on requested templates
        results_map = {}
        # Retrieve original request
        original_req = JOB_REQUESTS.get(job_id)
        requested_templates = original_req.templates if original_req else ["default"]

        for tmpl in requested_templates:
            if "soap" in tmpl:
                results_map[tmpl] = {"subjective": "Patient reports cough.", "assessment": "Viral URI"}
            elif "transcript" in tmpl:
                results_map[tmpl] = "Patient is a 45 year old male..."
            else:
                results_map[tmpl] = {"data": "Generic structured output"}

        job.output = ScribeOutput(results=results_map)
        job.completed_at = datetime.datetime.now(datetime.UTC).isoformat()
        job.status = JobStatus.COMPLETED
        
        # In a real app, here we would trigger the webhook
        # trigger_webhook(job)

    @staticmethod
    def get_job(job_id: str) -> Optional[JobResult]:
        return JOBS.get(job_id)

class SessionManager:
    @staticmethod
    def create_session(req: ScribeRequest) -> str:
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        SESSIONS[session_id] = {
            "req": req,
            "chunks": [],
            "created_at": datetime.datetime.utcnow()
        }
        return session_id

    @staticmethod
    def add_chunk(session_id: str, chunk: bytes, sequence: int):
        if session_id not in SESSIONS:
            raise KeyError("Session not found")
        
        # In a real system, you'd append to a file or stream to S3
        SESSIONS[session_id]["chunks"].append((sequence, chunk))

    @staticmethod
    def commit_session(session_id: str) -> JobResult:
        if session_id not in SESSIONS:
            raise KeyError("Session not found")
            
        session = SESSIONS[session_id]
        # Here we would stitch the chunks if needed
        # For now, just create the job
        job = JobManager.create_job(session["req"])
        
        # We do NOT start processing here anymore. The controller (FastAPI) will 
        # schedule it via BackgroundTasks to ensure it runs in the correct loop.
        
        return job
