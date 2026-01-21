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

## 7.2 Upload Modes Explained

### Single File Upload

Use single file upload when you have a complete, pre-recorded audio file. This is the simplest approach:

```
┌──────────────────────────────────────────────────┐
│                                                  │
│   Complete Audio File (e.g., consultation.wav)   │
│                                                  │
│   ──────────────────────────────────────────────▶│   Single Upload
│                                                  │
└──────────────────────────────────────────────────┘
```

- One HTTP request with the entire audio file
- Use `X-Upload-Type: complete` header
- File name is preserved as-is

### Chunked/Multiple File Upload

Use chunked upload for real-time streaming or when audio is captured in segments. This is common for:

- Live recording during patient consultations
- Progressive upload during long sessions
- Network resilience (smaller uploads are easier to retry)

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Chunk 0    │  │  Chunk 1    │  │  Chunk 2    │  │  Chunk 3    │
│  0-15 sec   │  │  15-30 sec  │  │  30-45 sec  │  │  45-60 sec  │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │                │
       ▼                ▼                ▼                ▼
    Upload 1         Upload 2         Upload 3         Upload 4
```

### File Naming Convention for Chunked Uploads

**CRITICAL:** When uploading multiple audio chunks, clients MUST use a consistent naming convention with numeric suffixes to indicate the correct playback order. The Scribe Service relies on this ordering to reconstruct the complete audio stream.

#### Naming Format

```
{base_name}_{sequence_number}.{extension}
```

| Component | Description | Example |
|-----------|-------------|---------|
| `base_name` | Descriptive identifier for the session/recording | `consultation`, `audio`, `recording` |
| `sequence_number` | Zero-based index indicating order | `0`, `1`, `2`, ... |
| `extension` | Audio format extension | `webm`, `wav`, `ogg` |

#### Examples

**Correct Naming:**
```
audio_0.webm    ← First chunk (0-15 seconds)
audio_1.webm    ← Second chunk (15-30 seconds)
audio_2.webm    ← Third chunk (30-45 seconds)
audio_3.webm    ← Fourth chunk (45-60 seconds)
```

**Also Acceptable:**
```
chunk_0.wav
chunk_1.wav
chunk_2.wav
```

```
consultation_recording_0.ogg
consultation_recording_1.ogg
consultation_recording_2.ogg
```

**Incorrect Naming (DO NOT USE):**
```
audio_first.webm     ← Non-numeric suffix
audio.webm           ← No sequence number
1_audio.webm         ← Prefix instead of suffix
audio_01.webm        ← Zero-padded (use _1 not _01)
```

#### Sending File Name with Upload

The file name is sent using standard HTTP file upload mechanisms, ensuring compatibility with cloud storage services (AWS S3, Google Cloud Storage, Azure Blob Storage) and standard file upload endpoints.

**Option 1: Multipart Form Data (Recommended)**

Standard multipart upload where the filename is part of the form field:

```http
POST /sessions/ses_abc123def456/audio HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxk

------WebKitFormBoundary7MA4YWxk
Content-Disposition: form-data; name="file"; filename="audio_0.webm"
Content-Type: audio/webm;codecs=opus

[binary audio data]
------WebKitFormBoundary7MA4YWxk--
```

**Option 2: Content-Disposition Header**

For raw binary uploads, use the standard `Content-Disposition` header:

```http
POST /sessions/ses_abc123def456/audio HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: audio/webm;codecs=opus
Content-Disposition: attachment; filename="audio_0.webm"
X-Chunk-Index: 0

[binary audio data]
```

**Option 3: Pre-signed URL Upload (Cloud Storage)**

When using pre-signed URLs (S3, GCS, Azure), the filename is typically part of the object key/path:

```http
PUT /bucket/sessions/ses_abc123def456/audio_0.webm?X-Amz-Signature=... HTTP/1.1
Host: s3.amazonaws.com
Content-Type: audio/webm;codecs=opus

[binary audio data]
```

The Scribe Service provides the `upload_url` with the appropriate path structure.

#### Why Order Matters

The Scribe Service processes audio chunks in sequence to:

1. **Maintain conversation continuity** - Medical conversations must be transcribed in order
2. **Preserve context** - Speaker diarization and context depend on temporal order
3. **Accurate timestamps** - Extracted information is time-referenced

If chunks are processed out of order, the resulting transcript and extractions will be incorrect or nonsensical.

#### Backend Processing Order

```
Files Received (any order):     Processing Order:
├── audio_2.webm                audio_0.webm → audio_1.webm → audio_2.webm → audio_3.webm
├── audio_0.webm                     │              │              │              │
├── audio_3.webm                     ▼              ▼              ▼              ▼
└── audio_1.webm                ┌──────────────────────────────────────────────────────┐
                                │          Concatenated Audio Stream                   │
                                └──────────────────────────────────────────────────────┘
                                                        │
                                                        ▼
                                              Transcription & Extraction
```

---

## 7.3 Upload Endpoint

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
