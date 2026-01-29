# MedScribe Alliance Protocol - Examples

This directory contains comprehensive examples and reference implementations for the MedScribe Alliance Protocol v0.1.

## Contents

### 📚 Documentation Examples

- **[discovery-document.json](discovery-document.json)** - Complete example of a discovery document response
- **[session-flow.md](session-flow.md)** - Step-by-step walkthrough of a complete session lifecycle
- **[webhook-payloads.json](webhook-payloads.json)** - Example webhook payloads for all event types

### 🖥️ Reference Server

- **[reference_server/](reference_server/)** - Complete FastAPI mock server implementation
  - Ready-to-run mock server for testing and development
  - All protocol endpoints implemented with mock data
  - Extensive TODO comments showing production implementation patterns
  - Docker support for easy deployment
  - Test suite and example client included

## Quick Start

### Run the Mock Server

```bash
cd reference_server
pip install -r requirements.txt
uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation.

### Test the Mock Server

```bash
cd reference_server
python test_server.py
```

### Use the Example Client

```bash
cd reference_server
python example_client.py
```

## Use Cases

### For EMR Developers

1. **Understanding the Protocol**
   - Read [session-flow.md](session-flow.md) for a complete walkthrough
   - Review [discovery-document.json](discovery-document.json) to understand service capabilities
   - Check [webhook-payloads.json](webhook-payloads.json) for event structures

2. **Testing Your Client**
   - Run the reference server locally
   - Point your client to `http://localhost:8000`
   - Test all endpoints without needing a production server

3. **Learning the API**
   - Use the [example_client.py](reference_server/example_client.py) as a starting point
   - Modify it to match your use case
   - Experiment with different parameters and flows

### For Scribe Service Providers

1. **Implementation Guide**
   - Review the [reference server code](reference_server/) structure
   - Follow the TODO comments for production implementation
   - Use the same request/response models

2. **Testing Your Implementation**
   - Compare your responses with the reference server
   - Use the test suite to validate compatibility
   - Verify your discovery document matches the schema

## File Descriptions

### discovery-document.json

A complete example of the discovery endpoint response showing:
- Service metadata
- Authentication configuration
- Available models and their capabilities
- Supported languages and audio formats
- Endpoint URLs

### session-flow.md

A narrative walkthrough of a typical session including:
- Creating a session
- Uploading audio files (chunked and single)
- Ending the session
- Polling for results
- Handling webhooks
- Error scenarios

### webhook-payloads.json

Example webhook payloads for all event types:
- `session.created` - Session initialization
- `session.processing` - Processing started
- `session.completed` - Successful completion
- `session.partial` - Partial results
- `session.failed` - Processing failure
- `session.expired` - Session timeout

### reference_server/

A complete FastAPI implementation with:
- **main.py** - Application entry point
- **models.py** - Pydantic models for all request/response schemas
- **routes/** - Endpoint implementations
  - discovery.py - Discovery endpoint
  - sessions.py - Session lifecycle
  - audio.py - Audio upload
  - templates.py - Template listing
- **test_server.py** - Automated test suite
- **example_client.py** - Complete client example
- **README.md** - Detailed server documentation
- **QUICKSTART.md** - Quick setup guide

## Testing Workflow

### 1. Start the Server

```bash
cd reference_server
uvicorn main:app --reload
```

### 2. Run Automated Tests

```bash
python test_server.py
```

Expected output:
```
============================================================
MedScribe Alliance Mock Server - Test Suite
============================================================
Testing discovery endpoint...
✓ Discovery endpoint works
Testing templates endpoint...
✓ Templates endpoint works (10 templates available)
Testing session lifecycle...
  ✓ Session created: ses_abc123...
  ✓ Uploaded audio_0.webm
  ✓ Uploaded audio_1.webm
  ✓ Session ended: Session ended. Processing started.
✓ Complete session lifecycle works
✓ All tests passed!
```

### 3. Try the Example Client

```bash
python example_client.py
```

This demonstrates a complete workflow with proper error handling.

## Development Tips

### Using the Mock Server for Development

1. **Local Development**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. **Docker Development**
   ```bash
   docker-compose up
   ```

3. **Custom Configuration**
   Set environment variables:
   ```bash
   export API_BASE_URL=https://your-domain.com
   export SUPPORT_EMAIL=support@your-domain.com
   uvicorn main:app
   ```

### Modifying Mock Responses

Edit the route files in `reference_server/routes/` to customize responses:

```python
# reference_server/routes/sessions.py

# Change the mock transcript
transcript="Your custom transcript here..."

# Change template extraction results
templates={
    "soap": {
        "status": "success",
        "data": {
            # Your custom data
        }
    }
}
```

### Adding New Endpoints

1. Create a new route file in `routes/`
2. Define your endpoint with FastAPI decorators
3. Add TODO comments for production implementation
4. Include the router in `main.py`

## Production Checklist

When converting the mock server to production:

- [ ] Add authentication middleware
- [ ] Implement database storage
- [ ] Integrate S3/GCS for audio files
- [ ] Add speech-to-text service
- [ ] Implement template extraction
- [ ] Set up message queue for async processing
- [ ] Add webhook delivery mechanism
- [ ] Implement rate limiting
- [ ] Add monitoring and logging
- [ ] Set up error tracking
- [ ] Configure HTTPS/TLS
- [ ] Add health checks and metrics
- [ ] Implement proper session expiry
- [ ] Add input validation and sanitization
- [ ] Set up CI/CD pipeline
- [ ] Write integration tests
- [ ] Document API versioning strategy

## Contributing

These examples are part of the MedScribe Alliance Protocol specification. To suggest improvements:

1. Review the [specification](../spec/)
2. Check the [schemas](../schemas/)
3. Submit feedback through the appropriate channels

## Additional Resources

- **Protocol Specification**: [../spec/](../spec/)
- **OpenAPI Schemas**: [../schemas/](../schemas/)
- **GitHub Repository**: [Link to repo]
- **Community Forum**: [Link to forum]

## License

See the LICENSE file in the protocol specification root directory.
