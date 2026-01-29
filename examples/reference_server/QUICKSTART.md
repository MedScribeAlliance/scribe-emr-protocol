# Quick Start Guide

Get the MedScribe Alliance Mock Server running in under 5 minutes.

## Option 1: Python (Recommended for Development)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
uvicorn main:app --reload
```

### Step 3: Verify Installation

Open your browser to http://localhost:8000/docs

Or run the test script:

```bash
python test_server.py
```

## Option 2: Docker

### Step 1: Build and Run

```bash
docker-compose up --build
```

### Step 2: Verify Installation

Open your browser to http://localhost:8000/docs

## Testing the API

### Using curl

```bash
# Get discovery document
curl http://localhost:8000/.well-known/medscribealliance | jq

# List templates
curl http://localhost:8000/v1/templates | jq

# Create a session
curl -X POST http://localhost:8000/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "templates": ["soap"],
    "upload_type": "single",
    "communication_protocol": "http"
  }' | jq

# Upload audio (replace SESSION_ID with actual session ID)
echo "mock audio data" > test_audio.webm
curl -X POST http://localhost:8000/v1/sessions/SESSION_ID/audio/audio_0.webm \
  -H "Content-Type: audio/webm" \
  --data-binary @test_audio.webm | jq

# End session
curl -X POST http://localhost:8000/v1/sessions/SESSION_ID/end \
  -H "Content-Type: application/json" \
  -d '{"audio_files_sent": 1}' | jq

# Check session status
curl http://localhost:8000/v1/sessions/SESSION_ID | jq
```

### Using Python

```python
import requests

# Create session
response = requests.post(
    "http://localhost:8000/v1/sessions",
    json={
        "templates": ["soap", "medications"],
        "upload_type": "chunked",
        "communication_protocol": "http"
    }
)
session = response.json()
print(f"Session ID: {session['session_id']}")

# Upload audio
with open("audio.webm", "rb") as f:
    requests.post(
        f"http://localhost:8000/v1/sessions/{session['session_id']}/audio/audio_0.webm",
        headers={"Content-Type": "audio/webm"},
        data=f.read()
    )

# End session
requests.post(
    f"http://localhost:8000/v1/sessions/{session['session_id']}/end",
    json={"audio_files_sent": 1}
)

# Get results
result = requests.get(
    f"http://localhost:8000/v1/sessions/{session['session_id']}"
)
print(result.json())
```

## Next Steps

- Read the [full documentation](README.md)
- Explore the [OpenAPI documentation](http://localhost:8000/docs)
- Check the [protocol specification](../../spec/)
- Review the [schemas](../../schemas/)

## Troubleshooting

### Port 8000 already in use

```bash
# Use a different port
uvicorn main:app --port 8001
```

### Module not found errors

```bash
# Make sure you're in the correct directory
cd scribe_emr_protocol/examples/reference_server

# Reinstall dependencies
pip install -r requirements.txt
```

### Docker issues

```bash
# Rebuild the container
docker-compose down
docker-compose up --build
```
