# MedScribe Alliance Protocol - Reference Mock Server

This is a complete mock implementation of the **MedScribe Alliance Protocol v0.1** for testing and development purposes. 
[[####note: it's not production ready server, it's just and reference implementation in FAST API server.]]

## Overview

This reference server implements all required endpoints of the MedScribe Alliance Protocol with mock responses. It is designed to:

- Help EMR developers understand the protocol structure
- Enable client-side testing without a full backend implementation
- Serve as a template for implementing production servers
- Demonstrate proper request/response formats and status codes

## Features

### Implemented Endpoints

#### Discovery
- `GET /.well-known/medscribealliance` - Service discovery document

#### Sessions
- `POST /v1/sessions` - Create new voice capture session
- `GET /v1/sessions/{session_id}` - Get session status and results
- `POST /v1/sessions/{session_id}/end` - End session and trigger processing

#### Audio Upload
- `POST /v1/sessions/{session_id}/audio/{file_name}` - Upload audio files
- `GET /v1/sessions/{session_id}/audio/credentials` - Get S3 credentials (stub)

#### Templates
- `GET /v1/templates` - List available extraction templates

### Mock Data

All endpoints return realistic mock data including:
- Multiple session statuses (created, processing, completed, partial, expired)
- Sample SOAP notes and medication lists
- Multiple model configurations (lite, pro)
- Various audio format support
- Multiple language support

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository or navigate to this directory:
   ```bash
   cd scribe_emr_protocol/examples/reference_server
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

### Development Mode

Start the server with auto-reload:

```bash
uvicorn main:app --reload
```

The server will start on `http://localhost:8000`

### Custom Host/Port

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Example Usage

### 1. Get Discovery Document

```bash
curl http://localhost:8000/.well-known/medscribealliance
```

### 2. List Available Templates

```bash
curl http://localhost:8000/v1/templates
```

### 3. Create a Session

```bash
curl -X POST http://localhost:8000/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "templates": ["soap", "medications"],
    "model": "pro",
    "upload_type": "chunked",
    "communication_protocol": "http",
    "additional_data": {
      "emr_encounter_id": "enc_123"
    }
  }'
```

### 4. Upload Audio

```bash
# Upload first audio chunk
curl -X POST http://localhost:8000/v1/sessions/ses_abc123/audio/audio_0.webm \
  -H "Content-Type: audio/webm;codecs=opus" \
  --data-binary @audio_chunk_0.webm

# Upload second audio chunk
curl -X POST http://localhost:8000/v1/sessions/ses_abc123/audio/audio_1.webm \
  -H "Content-Type: audio/webm;codecs=opus" \
  --data-binary @audio_chunk_1.webm
```

### 5. End Session

```bash
curl -X POST http://localhost:8000/v1/sessions/ses_abc123/end \
  -H "Content-Type: application/json" \
  -d '{
    "audio_files_sent": 2
  }'
```

### 6. Check Session Status

```bash
curl http://localhost:8000/v1/sessions/ses_abc123
```

## Architecture

```
reference_server/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models for all request/response schemas
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── routes/             # Endpoint implementations
    ├── __init__.py
    ├── discovery.py    # Discovery endpoint
    ├── sessions.py     # Session lifecycle endpoints
    ├── audio.py        # Audio upload endpoints
    └── templates.py    # Template listing endpoint
```

## TODO Comments

Throughout the codebase, `TODO` comments indicate where production implementations would differ from the mock server. Key areas include:

### Authentication
- API key validation
- OIDC token verification
- User/EMR permission checks

### Storage
- S3/GCS integration for audio files
- Database for session metadata
- Redis/Memcached for caching

### Processing
- Message queue integration (SQS, Kafka)
- Asynchronous processing pipeline
- Real-time transcription
- Template extraction logic

### Webhooks
- Webhook registration and delivery
- Retry logic and dead letter queues
- Webhook signature validation

### Validation
- Template ID validation against user permissions
- Rate limiting and quotas
- File size and format validation
- Session expiry checking

## Testing

You can test the mock server with:

1. **Postman/Insomnia**: Import the OpenAPI spec from `/docs` endpoint
2. **curl**: Use the example commands above
3. **Python requests**:

```python
import requests

# Get discovery
response = requests.get("http://localhost:8000/.well-known/medscribealliance")
print(response.json())

# Create session
session_response = requests.post(
    "http://localhost:8000/v1/sessions",
    json={
        "templates": ["soap"],
        "upload_type": "single",
        "communication_protocol": "http"
    }
)
print(session_response.json())
```

## Limitations

This is a **mock server** for development and testing only:

- ❌ No authentication or authorization
- ❌ In-memory storage (data lost on restart)
- ❌ No actual audio processing
- ❌ No webhook delivery
- ❌ No rate limiting
- ❌ No production-grade error handling
- ❌ No database persistence

## Production Implementation Guide

To convert this mock server to production:

1. **Add Authentication**
   - Implement API key middleware
   - Add OIDC token validation
   - Check user permissions

2. **Add Storage**
   - Integrate S3/GCS for audio files
   - Add PostgreSQL/MySQL for metadata
   - Implement Redis for caching

3. **Add Processing**
   - Integrate speech-to-text service
   - Implement template extraction logic
   - Add message queue for async processing

4. **Add Webhooks**
   - Implement webhook registration
   - Add delivery mechanism with retries
   - Generate webhook signatures

5. **Add Monitoring**
   - Structured logging
   - Metrics collection (Prometheus)
   - Error tracking (Sentry)
   - Distributed tracing

6. **Add Security**
   - HTTPS/TLS
   - Request signing
   - Rate limiting
   - Input validation

## Contributing

This reference server is part of the MedScribe Alliance Protocol specification. For improvements or bug reports, please refer to the main protocol documentation.

## License

See the LICENSE file in the protocol specification root directory.

## Support

For questions about the protocol or this reference implementation, refer to:
- Protocol specification: `../spec/`
- Schema documentation: `../schemas/`
- Example payloads: `../examples/`
