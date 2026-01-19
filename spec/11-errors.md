# 11. Error Handling

**MedScribeAlliance Protocol Specification v0.1**

---

## 11.1 Error Response Format

All error responses MUST follow this structure:

```json
{
  "error": {
    "code": "error_code",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `error.code` | string | Yes | Machine-readable error code |
| `error.message` | string | Yes | Human-readable description |
| `error.details` | object | No | Additional error context |

---

## 11.2 Standard Error Codes

### Authentication Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `authentication_failed` | 401 | Invalid or missing credentials |
| `token_expired` | 401 | Access token has expired |
| `invalid_api_key` | 401 | API key is invalid |

### Authorization Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `forbidden` | 403 | Insufficient permissions |
| `rate_limit_exceeded` | 429 | Too many requests |

### Resource Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `session_not_found` | 404 | Session does not exist |
| `template_not_found` | 404 | Requested template not available |
| `webhook_not_found` | 404 | Webhook does not exist |
| `session_expired` | 410 | Session has expired |

### Request Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `invalid_request` | 400 | Malformed request |
| `invalid_audio_format` | 400 | Unsupported audio format |
| `chunk_too_large` | 400 | Audio chunk exceeds maximum duration |
| `invalid_template` | 400 | Invalid template specified |
| `missing_required_field` | 400 | Required field not provided |

### Processing Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `processing_failed` | 500 | Internal processing error |
| `audio_quality_poor` | 422 | Audio too noisy or unclear |
| `audio_too_short` | 422 | Insufficient audio for processing |
| `language_unsupported` | 422 | Detected language not supported |

### Server Errors

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `internal_error` | 500 | Unexpected server error |
| `service_unavailable` | 503 | Service temporarily unavailable |

---

## 11.3 HTTP Status Codes

| Status | Category | Usage |
|--------|----------|-------|
| 200 | Success | Successful GET, PUT requests |
| 201 | Success | Successful resource creation (POST) |
| 204 | Success | Successful deletion (no content) |
| 400 | Client Error | Invalid request syntax or parameters |
| 401 | Client Error | Authentication failure |
| 403 | Client Error | Authorization failure |
| 404 | Client Error | Resource not found |
| 410 | Client Error | Resource gone (expired) |
| 422 | Client Error | Unprocessable entity (validation failed) |
| 429 | Client Error | Rate limit exceeded |
| 500 | Server Error | Internal server error |
| 503 | Server Error | Service unavailable |

---

## 11.4 Error Examples

### Authentication Failed

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": {
    "code": "authentication_failed",
    "message": "Invalid API key provided"
  }
}
```

### Invalid Audio Format

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "invalid_audio_format",
    "message": "Audio format 'audio/mp3' is not supported",
    "details": {
      "provided_format": "audio/mp3",
      "supported_formats": [
        "audio/webm;codecs=opus",
        "audio/wav",
        "audio/ogg"
      ]
    }
  }
}
```

### Chunk Too Large

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "chunk_too_large",
    "message": "Audio chunk exceeds maximum duration of 20 seconds",
    "details": {
      "chunk_duration_seconds": 25.4,
      "max_duration_seconds": 20
    }
  }
}
```

### Session Not Found

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": {
    "code": "session_not_found",
    "message": "Session 'ses_invalid123' does not exist",
    "details": {
      "session_id": "ses_invalid123"
    }
  }
}
```

### Session Expired

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "error": {
    "code": "session_expired",
    "message": "Session 'ses_abc123def456' has expired",
    "details": {
      "session_id": "ses_abc123def456",
      "expired_at": "2025-01-19T11:30:00Z"
    }
  }
}
```

### Rate Limit Exceeded

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 60

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded. Please retry after 60 seconds.",
    "details": {
      "limit": 100,
      "window": "1 minute",
      "retry_after_seconds": 60
    }
  }
}
```

### Processing Failed

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": {
    "code": "processing_failed",
    "message": "Unable to process audio due to internal error",
    "details": {
      "session_id": "ses_abc123def456",
      "request_id": "req_xyz789"
    }
  }
}
```

### Audio Quality Poor

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json

{
  "error": {
    "code": "audio_quality_poor",
    "message": "Audio quality is too low for accurate transcription",
    "details": {
      "session_id": "ses_abc123def456",
      "quality_score": 0.23,
      "minimum_required": 0.5,
      "suggestions": [
        "Reduce background noise",
        "Speak closer to the microphone",
        "Use a higher quality microphone"
      ]
    }
  }
}
```

---

## 11.5 Error Handling Best Practices

### For EMR Clients

1. **Check HTTP status first**
   ```python
   if response.status_code >= 400:
       error = response.json().get('error', {})
       handle_error(error['code'], error['message'])
   ```

2. **Handle specific error codes**
   ```python
   if error['code'] == 'session_expired':
       create_new_session()
   elif error['code'] == 'rate_limit_exceeded':
       wait_and_retry(error['details']['retry_after_seconds'])
   ```

3. **Log errors for debugging**
   ```python
   logger.error(f"API error: {error['code']} - {error['message']}", 
                extra={'details': error.get('details')})
   ```

4. **Show user-friendly messages**
   - Don't expose raw error codes to users
   - Provide actionable guidance when possible

5. **Implement retry logic**
   - Retry on 429, 500, 503
   - Don't retry on 400, 401, 403, 404

### For Scribe Services

1. **Use consistent error format** across all endpoints
2. **Include helpful details** when available
3. **Log all errors** with request context
4. **Return appropriate HTTP status codes**
5. **Include `Retry-After` header** for rate limits

---

## 11.6 Retry Guidelines

### Retryable Errors

| Code | Retry? | Strategy |
|------|--------|----------|
| `rate_limit_exceeded` | Yes | Wait for `Retry-After`, then retry |
| `service_unavailable` | Yes | Exponential backoff |
| `internal_error` | Maybe | Retry once, then fail |
| `processing_failed` | No | Report to user |
| `authentication_failed` | No | Check credentials |
| `session_not_found` | No | Session doesn't exist |

### Exponential Backoff

```python
import time
import random

def retry_with_backoff(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except RetryableError as e:
            if attempt == max_retries - 1:
                raise
            
            # Exponential backoff with jitter
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

---

**Previous:** [Webhooks](./10-webhooks.md) | **Next:** [Security](./12-security.md)
