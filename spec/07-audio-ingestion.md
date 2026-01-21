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
- Requires `upload_type: "single"` in session creation request
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

## 7.3 Upload URL

The upload URL is provided dynamically in the session creation response (`upload_url` field). This URL is where clients upload audio files for the session.

### Dynamic Upload URL

The `upload_url` returned by `POST /sessions` can be:

| URL Type | Description | Example |
|----------|-------------|---------|
| **Scribe API Endpoint** | Direct upload to Scribe Service | `https://api.scribe.example.com/v1/sessions/ses_abc123/audio` |
| **AWS S3 Pre-signed URL** | Direct upload to S3 bucket | `https://bucket.s3.amazonaws.com/sessions/ses_abc123/?X-Amz-Signature=...` |
| **Google Cloud Storage** | Direct upload to GCS bucket | `https://storage.googleapis.com/bucket/sessions/ses_abc123/?X-Goog-Signature=...` |
| **Azure Blob Storage** | Direct upload to Azure container | `https://account.blob.core.windows.net/container/ses_abc123?sv=...&sig=...` |

### Session Creation Response

```http
POST /sessions HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: application/json

{
  "templates": ["soap", "medications"],
  "upload_type": "chunked"
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "created",
  "created_at": "2025-01-19T10:30:00Z",
  "expires_at": "2025-01-19T11:30:00Z",
  "upload_url": "https://storage.googleapis.com/scribe-uploads/ses_abc123def456/?X-Goog-Signature=..."
}
```

**Important:** Clients MUST use the exact `upload_url` provided in the response. Do not construct or modify this URL.

---

## 7.4 Chunked Upload

For streaming or progressive audio capture. Ideal for real-time recording scenarios.

### Requirements

- Each chunk MUST be ≤20 seconds duration
- Chunks MUST be uploaded with proper file naming (see [File Naming Convention](#file-naming-convention-for-chunked-uploads))
- All chunks MUST use the same audio format

### Upload to Pre-signed URL (Cloud Storage)

When `upload_url` points to cloud storage, upload each chunk as a separate object:

```http
PUT {upload_url}/audio_0.webm HTTP/1.1
Content-Type: audio/webm;codecs=opus

[binary audio data for chunk 0]
```

```http
PUT {upload_url}/audio_1.webm HTTP/1.1
Content-Type: audio/webm;codecs=opus

[binary audio data for chunk 1]
```

### Upload to Scribe API Endpoint

When `upload_url` points to the Scribe API, use multipart form data:

```http
POST {upload_url} HTTP/1.1
Content-Type: multipart/form-data; boundary=----FormBoundary

------FormBoundary
Content-Disposition: form-data; name="file"; filename="audio_0.webm"
Content-Type: audio/webm;codecs=opus

[binary audio data]
------FormBoundary--
```

### Multi-Chunk Upload Flow

```
Session Created → upload_url: https://storage.example.com/ses_abc123/

Chunk 0: PUT {upload_url}/audio_0.webm  [0-15 seconds]
         → 200 OK

Chunk 1: PUT {upload_url}/audio_1.webm  [15-30 seconds]
         → 200 OK

Chunk 2: PUT {upload_url}/audio_2.webm  [30-42 seconds]
         → 200 OK

End:     POST /sessions/ses_abc123/end
         → 202 Accepted, status: processing
```

---

## 7.5 Single File Upload

For complete audio file upload after recording is finished. Requires `upload_type: "single"` to be specified during session creation.

### Session Creation for Single Upload

```http
POST /sessions HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: application/json

{
  "templates": ["soap", "medications"],
  "upload_type": "single"
}
```

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "created",
  "upload_url": "https://storage.googleapis.com/scribe-uploads/ses_abc123def456/recording.webm?X-Goog-Signature=..."
}
```

### Upload to Pre-signed URL (Cloud Storage)

```http
PUT {upload_url} HTTP/1.1
Content-Type: audio/wav

[binary audio data]
```

### Upload to Scribe API Endpoint

```http
POST {upload_url} HTTP/1.1
Content-Type: multipart/form-data; boundary=----FormBoundary

------FormBoundary
Content-Disposition: form-data; name="file"; filename="consultation.wav"
Content-Type: audio/wav

[binary audio data]
------FormBoundary--
```

### Single File Upload Flow

```
Session Created → upload_url: https://storage.example.com/ses_abc123/recording.webm?sig=...

Upload:  PUT {upload_url}  [complete audio file]
         → 200 OK

End:     POST /sessions/ses_abc123/end
         → 202 Accepted, status: processing
```

---

## 7.6 Audio Format Requirements

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

Clients SHOULD validate audio format before uploading by checking supported formats in the discovery document.

**Note:** When uploading to pre-signed URLs (S3, GCS, Azure), format validation errors are returned directly by the cloud storage provider in their native format. The Scribe Service cannot control these error responses. Clients should handle standard HTTP 4xx errors from the storage provider.

Format validation by the Scribe Service occurs during processing. Invalid formats will result in a `failed` session status with an appropriate error message.

---

## 7.7 Chunk Duration Limits

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

### Chunk Duration Validation

Chunk duration is validated by the Scribe Service during processing, not during upload. If any chunk exceeds the maximum duration:

- The session status will reflect the error
- Processing may result in `partial` or `failed` status
- The error details are available via `GET /sessions/{id}` or webhook notification

Clients SHOULD validate chunk duration before uploading by checking `max_chunk_duration_seconds` in the discovery document.

---

## 7.8 Upload Errors

Since audio uploads typically go to cloud storage providers (S3, GCS, Azure) or standard file upload servers, error responses follow the provider's native format. The Scribe Service cannot control these responses.

### Common HTTP Errors

| Status Code | Description | Common Causes |
|-------------|-------------|---------------|
| `400 Bad Request` | Invalid request | Malformed request, invalid headers |
| `401 Unauthorized` | Authentication failed | Expired or invalid pre-signed URL |
| `403 Forbidden` | Access denied | Insufficient permissions, URL signature mismatch |
| `404 Not Found` | Resource not found | Invalid upload path, session doesn't exist |
| `413 Payload Too Large` | File too large | Exceeds storage provider limits |

### Client Handling

Clients SHOULD:

1. **Retry on transient errors** (5xx status codes) with exponential backoff
2. **Check session status** via `GET /sessions/{id}` if upload fails to determine next steps
3. **Request new session** if pre-signed URL has expired (401/403 errors)
4. **Log error responses** for debugging, as formats vary by provider

---

## 7.9 Best Practices

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
