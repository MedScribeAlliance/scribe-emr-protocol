# 7. Audio Ingestion

**MedScribeAlliance Protocol Specification v0.1**

---

## 7.1 Overview

Audio upload is the core data transfer mechanism in the protocol. Scribe Services MUST support at least one upload method:

| Method | Description | Use Case |
|--------|-------------|----------|
| **Chunked** | Multiple sequential uploads | Streaming, real-time capture |
| **Single** | One complete file upload | Post-recording upload |

The discovery document declares which methods are supported:

```json
{
  "capabilities": {
    "upload_methods": ["chunked", "single"]
  }
}
```

---

## 7.2 Upload Endpoint

**Endpoint:** `POST /sessions/{session_id}/audio`

**Required:** Yes

Uploads audio data to an active session.

---

## 7.3 Chunked Upload

For streaming or progressive audio capture. Ideal for real-time recording scenarios.

### Requirements

- Each chunk MUST be ≤20 seconds duration
- Chunks MUST be uploaded sequentially (by `X-Chunk-Index`)
- All chunks MUST use the same audio format

### Request

```http
POST /sessions/ses_abc123def456/audio HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: audio/webm;codecs=opus
X-Chunk-Index: 0

[binary audio data]
```

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | Audio MIME type (must match discovery) |
| `X-Chunk-Index` | Yes | Zero-based chunk sequence number |
| `Content-Length` | Yes | Size of audio data in bytes |

### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "chunk_index": 0,
  "chunk_duration_ms": 15000,
  "total_duration_ms": 15000,
  "status": "received"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Session identifier |
| `chunk_index` | integer | Received chunk index |
| `chunk_duration_ms` | integer | Duration of this chunk |
| `total_duration_ms` | integer | Total audio duration so far |
| `status` | string | `"received"` on success |

### Multi-Chunk Example

```
Chunk 0: POST /sessions/{id}/audio  X-Chunk-Index: 0  [0-15 seconds]
         → 200 OK, total_duration_ms: 15000

Chunk 1: POST /sessions/{id}/audio  X-Chunk-Index: 1  [15-30 seconds]
         → 200 OK, total_duration_ms: 30000

Chunk 2: POST /sessions/{id}/audio  X-Chunk-Index: 2  [30-42 seconds]
         → 200 OK, total_duration_ms: 42000

End:     POST /sessions/{id}/end
         → 200 OK, status: processing
```

---

## 7.4 Single File Upload

For complete audio file upload after recording is finished.

### Request

```http
POST /sessions/ses_abc123def456/audio HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: audio/wav
X-Upload-Type: complete

[binary audio data]
```

### Headers

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | Audio MIME type (must match discovery) |
| `X-Upload-Type` | Yes | Must be `"complete"` for single upload |
| `Content-Length` | Yes | Size of audio data in bytes |

### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "duration_ms": 180000,
  "status": "received"
}
```

---

## 7.5 Audio Format Requirements

### Supported Formats

Formats are declared in the discovery document:

```json
{
  "capabilities": {
    "audio_formats": [
      "audio/webm;codecs=opus",
      "audio/wav",
      "audio/ogg"
    ]
  }
}
```

### Common Formats

| Format | MIME Type | Notes |
|--------|-----------|-------|
| WebM Opus | `audio/webm;codecs=opus` | Recommended for browser |
| WAV | `audio/wav` | Uncompressed, reliable |
| OGG Vorbis | `audio/ogg` | Good compression |
| OGG Opus | `audio/ogg;codecs=opus` | Best compression |

### Recommended Encoding

| Parameter | Recommendation |
|-----------|----------------|
| Sample rate | 16kHz or higher |
| Channels | Mono (1 channel) |
| Bit depth | 16-bit (for WAV) |
| Bitrate | 32kbps+ (for compressed) |

### Format Validation

If an unsupported format is uploaded:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "invalid_audio_format",
    "message": "Audio format 'audio/mp3' is not supported",
    "details": {
      "provided_format": "audio/mp3",
      "supported_formats": ["audio/webm;codecs=opus", "audio/wav"]
    }
  }
}
```

---

## 7.6 Chunk Duration Limits

### Maximum Chunk Duration

The discovery document specifies maximum chunk duration:

```json
{
  "capabilities": {
    "max_chunk_duration_seconds": 20
  }
}
```

Protocol RECOMMENDS maximum of 20 seconds per chunk.

### Chunk Too Large Error

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "chunk_too_large",
    "message": "Audio chunk exceeds maximum duration",
    "details": {
      "chunk_duration_seconds": 25,
      "max_duration_seconds": 20
    }
  }
}
```

---

## 7.7 Upload Errors

### Session Not Found

```http
HTTP/1.1 404 Not Found

{
  "error": {
    "code": "session_not_found",
    "message": "Session 'ses_invalid' does not exist"
  }
}
```

### Session Already Ended

```http
HTTP/1.1 400 Bad Request

{
  "error": {
    "code": "invalid_request",
    "message": "Cannot upload audio to ended session"
  }
}
```

### Session Expired

```http
HTTP/1.1 410 Gone

{
  "error": {
    "code": "session_expired",
    "message": "Session has expired"
  }
}
```

### Chunk Out of Order

```http
HTTP/1.1 400 Bad Request

{
  "error": {
    "code": "invalid_request",
    "message": "Chunk index 5 received, expected 3",
    "details": {
      "received_index": 5,
      "expected_index": 3
    }
  }
}
```

---

## 7.8 Best Practices

### For EMR Clients

1. **Check supported formats** before recording
   ```javascript
   const formats = discovery.capabilities.audio_formats;
   const preferred = formats.includes('audio/webm;codecs=opus') 
     ? 'audio/webm;codecs=opus' 
     : formats[0];
   ```

2. **Use chunked upload** for real-time capture
   - Better user experience (progress feedback)
   - Resilient to network interruptions
   - Enables real-time transcription (if supported)

3. **Use single upload** for pre-recorded audio
   - Simpler implementation
   - Atomic upload (all or nothing)

4. **Respect chunk duration limits**
   - Split audio at natural boundaries when possible
   - Don't split mid-word if avoidable

5. **Handle upload failures gracefully**
   - Retry transient failures
   - Show clear error messages to users

### For Scribe Services

1. **Validate audio format** on first byte
2. **Acknowledge chunks quickly** (before processing)
3. **Handle out-of-order chunks** gracefully if possible
4. **Provide clear duration feedback** in responses

---

**Previous:** [Sessions](./06-sessions.md) | **Next:** [Templates](./08-templates.md)
