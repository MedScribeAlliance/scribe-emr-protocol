from fastapi.testclient import TestClient
from src.server import app
from src.models import JobStatus
import time
import pytest
import json

client = TestClient(app)

def test_handshake():
    payload = {
        "protocolVersion": "2024-01-01",
        "clientInfo": {"name": "TestClient", "version": "1.0"}
    }
    response = client.post("/initialize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["protocolVersion"] == "2024-01-01"
    assert data["serverInfo"]["name"] == "SEP Reference Implementation"
    assert len(data["templates"]) > 0
    assert data["templates"][0]["id"] == "soap_v1"

def test_sync_processing():
    req_payload = {
        "templates": ["soap_v1", "transcript_v1"],
        "context": {"patient": {"name": "Test Patient"}}
    }
    
    # Create dummy audio file
    files = {'file': ('test.wav', b'fakeaudiobytes', 'audio/wav')}
    data = {'request': json.dumps(req_payload)}
    
    response = client.post("/process", data=data, files=files)
    assert response.status_code == 200
    result = response.json()
    
    # Sync should return completed result immediately (after simulated blocking)
    assert result["status"] == JobStatus.COMPLETED
    # Check for multi-template results
    assert "soap_v1" in result["output"]["results"]
    assert "transcript_v1" in result["output"]["results"]

def test_async_processing():
    req_payload = {
        "templates": ["soap_v1"],
        "config": {"webhook_url": "http://localhost/hook"}
    }
    files = {'file': ('test.wav', b'fakeaudiobytes', 'audio/wav')}
    data = {'request': json.dumps(req_payload)}
    
    response = client.post("/process/async", data=data, files=files)
    assert response.status_code == 202
    result = response.json()
    job_id = result["job_id"]
    assert result["status"] == JobStatus.QUEUED
    
    # Poll for completion (give background task time to run)
    time.sleep(4) 
    
    status_response = client.get(f"/jobs/{job_id}")
    assert status_response.status_code == 200
    final_state = status_response.json()
    assert final_state["status"] == JobStatus.COMPLETED
    assert "soap_v1" in final_state["output"]["results"]

def test_chunked_session():
    # 1. Create Session
    req_payload = {"templates": ["referral_v1"]}
    resp1 = client.post("/session", json=req_payload)
    assert resp1.status_code == 201
    session_id = resp1.json()["session_id"]
    
    # 2. Upload Chunk
    files = {'file': ('chunk.wav', b'chunkbytes', 'audio/wav')}
    resp2 = client.post(
        f"/session/{session_id}/audio", 
        files=files,
        headers={"x-audio-sequence": "0"}
    )
    assert resp2.status_code == 200
    
    # 3. Commit
    resp3 = client.post(f"/session/{session_id}/commit")
    assert resp3.status_code == 202
    job_id = resp3.json()["job_id"]
    
    # 4. Verify Job Created
    resp4 = client.get(f"/jobs/{job_id}")
    assert resp4.status_code == 200
