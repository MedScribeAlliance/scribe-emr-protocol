# 6. Session Lifecycle

**MedScribeAlliance Protocol Specification v0.1**

---

A **session** represents a single voice capture and extraction workflow. Sessions have a defined lifecycle from creation to completion or expiry.

## 6.1 Session States

```
                    ┌─────────────┐
                    │             │
         ┌─────────▶│   CREATED   │
         │          │             │
         │          └──────┬──────┘
         │                 │
         │                 │ Audio uploaded
         │                 ▼
         │          ┌─────────────┐
         │          │             │
         │          │  RECORDING  │
         │          │             │
         │          └──────┬──────┘
         │                 │
    Timeout                │ POST /sessions/{id}/end
         │                 ▼
         │          ┌─────────────┐
         │          │             │
         │          │ PROCESSING  │
         │          │             │
         │          └──────┬──────┘
         │                 │
         │        ┌────────┼────────┐
         │        │        │        │
         │        ▼        ▼        ▼
         │  ┌─────────┐ ┌─────────┐ ┌─────────┐
         │  │COMPLETED│ │ PARTIAL │ │ FAILED  │
         │  └─────────┘ └─────────┘ └─────────┘
         │
         ▼
   ┌───────────┐
   │  EXPIRED  │
   └───────────┘
```

| State | Description |
|-------|-------------|
| `created` | Session created, awaiting audio upload |
| `recording` | Audio upload in progress |
| `processing` | Session ended, extraction in progress |
| `completed` | Extraction complete, all results available |
| `partial` | Extraction complete, partial results available due to audio or processing issues |
| `failed` | Processing failed entirely |
| `expired` | Session timed out before completion |

---

## 6.2 Create Session

**Endpoint:** `POST /sessions`

**Required:** Yes

Creates a new voice capture session.

### Request

```http
POST /sessions HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: application/json

{
  "templates": ["soap", "medications"],
  "model": "pro",
  "language_hint": "hi",
  "transcript_language": "en",
  "upload_type": "chunked",
  "additional_data": {
    "emr_encounter_id": "enc_123",
    "emr_patient_id": "pat_456"
  }
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `templates` | array | Yes | Template IDs to extract (see [Templates](./08-templates.md)) |
| `model` | string | No | Model ID from discovery. Default: service decides |
| `language_hint` | string | No | ISO 639-1 language hint for audio input. Auto-detected if not provided |
| `transcript_language` | string | No | ISO 639-1 code for transcript output language. Defaults to detected input language |
| `upload_type` | string | No | Audio upload method: `chunked` or `single`. Default: `chunked` |
| `additional_data` | object | No | Pass-through data returned in webhooks and responses |

### Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "created",
  "created_at": "2025-01-19T10:30:00Z",
  "expires_at": "2025-01-19T11:30:00Z",
  "upload_url": "https://api.scribe.example.com/v1/sessions/ses_abc123def456/audio"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique session identifier |
| `status` | string | Current session state |
| `created_at` | string | ISO 8601 creation timestamp |
| `expires_at` | string | ISO 8601 expiry timestamp |
| `upload_url` | string | Absolute URL for audio upload |

### Session ID Format

Session IDs SHOULD:

- Be prefixed with `ses_` for easy identification
- Be URL-safe (alphanumeric, hyphens, underscores)
- Be unique across all sessions

---

## 6.3 Get Session Status

**Endpoint:** `GET /sessions/{session_id}`

**Required:** Yes

Retrieves session status and extraction results if complete.

### Request

```http
GET /sessions/ses_abc123def456 HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
```

### Response (Processing)

```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "processing",
  "created_at": "2025-01-19T10:30:00Z",
  "expires_at": "2025-01-19T11:30:00Z",
  "audio_files_received": 3,
  "audio_files": ["audio_0.webm", "audio_1.webm", "audio_2.webm"],
  "additional_data": {
    "emr_encounter_id": "enc_123"
  },
  "transcript": "Doctor: Good morning...\nPatient: I've been having..."
}
```

**Note:** The `transcript` field is included in processing responses when transcription is complete but template extraction is still in progress.

### Response (Completed)

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "completed",
  "created_at": "2025-01-19T10:30:00Z",
  "completed_at": "2025-01-19T10:35:00Z",
  "model_used": "pro",
  "language_detected": "hi",
  "audio_files_received": 3,
  "audio_files": ["audio_0.webm", "audio_1.webm", "audio_2.webm"],
  "additional_data": {
    "emr_encounter_id": "enc_123"
  },
  "templates": {
    "soap": {
      "status": "success",
      "data": {
        "subjective": "...",
        "objective": "...",
        "assessment": "...",
        "plan": "..."
      }
    },
    "medications": {
      "status": "success",
      "data": [...]
    }
  },
  "transcript": "Doctor: ...\nPatient: ..."
}
```

### Response (Partial)

Returned when the system cannot process all audio or templates due to client-side issues (e.g., poor audio quality in segments) or backend processing errors, but partial results are available.

```http
HTTP/1.1 206 Partial Content
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "partial",
  "created_at": "2025-01-19T10:30:00Z",
  "completed_at": "2025-01-19T10:35:00Z",
  "model_used": "pro",
  "language_detected": "hi",
  "audio_files_received": 3,
  "audio_files": ["audio_0.webm", "audio_1.webm", "audio_2.webm"],
  "audio_files_processed": 2,
  "additional_data": {
    "emr_encounter_id": "enc_123"
  },
  "templates": {
    "soap": {
      "status": "success",
      "data": {
        "subjective": "...",
        "objective": "...",
        "assessment": "...",
        "plan": "..."
      }
    },
    "medications": {
      "status": "failed",
      "error": {
        "code": "extraction_failed",
        "message": "Could not extract medication information from audio"
      }
    }
  },
  "transcript": "Doctor: ...\nPatient: ...",
  "processing_errors": [
    {
      "type": "audio_file_skipped",
      "message": "Audio file audio_2.webm skipped due to poor quality",
      "file": "audio_2.webm"
    }
  ]
}
```

**Partial Response Scenarios:**

| Scenario | Description |
|----------|-------------|
| Audio quality issues | Some audio segments were unprocessable |
| Template extraction failure | One or more templates failed while others succeeded |
| Timeout during processing | Processing timed out before all templates completed |
| Backend resource limits | Partial processing due to resource constraints |

See [Extraction](./09-extraction.md) for full response structure.

---

## 6.4 End Session

**Endpoint:** `POST /sessions/{session_id}/end`

**Required:** Yes

Explicitly ends a session and triggers processing.

### Request

```http
POST /sessions/ses_abc123def456/end HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
```

### Response

```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "processing",
  "message": "Session ended. Processing started.",
  "audio_files_received": 3,
  "audio_files": [
    "chunk_0.webm",
    "chunk_1.webm",
    "chunk_2.webm"
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique session identifier |
| `status` | string | Current session state (`processing`) |
| `message` | string | Human-readable status message |
| `audio_files_received` | integer | Total number of audio files successfully received |
| `audio_files` | array | List of audio file names received for this session |

### Important Notes

- EMR clients MUST explicitly end sessions
- Ending a session triggers processing; no more audio can be uploaded
- Auto-end behavior (silence detection, etc.) is a scribe vendor capability, not protocol-mandated

---

## 6.5 Session Expiry

Sessions that are not explicitly ended will expire based on scribe service configuration.

### Expiry Behavior

- Maximum session duration is defined per model in discovery document
- Sessions MUST auto-expire if not ended within the limit
- Expired sessions MUST NOT accept further audio uploads
- Scribe Services SHOULD send `session.expired` webhook on expiry

### Expiry Example

If `max_session_duration_seconds` is 3600 (1 hour):

```
Session created:  2025-01-19T10:00:00Z
Expires at:       2025-01-19T11:00:00Z

If no /end call by 11:00:00Z → status becomes "expired"
```

### Accessing Expired Sessions

When a session expires, the response includes all data that was received and any partial processing that may have occurred before expiry.

```http
GET /sessions/ses_expired123
```

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "session_id": "ses_expired123",
  "status": "expired",
  "created_at": "2025-01-19T10:00:00Z",
  "expired_at": "2025-01-19T11:00:00Z",
  "message": "Session expired before processing was initiated",
  "audio_files_received": 5,
  "audio_files": [
    "audio_0.webm",
    "audio_1.webm",
    "audio_2.webm",
    "audio_3.webm",
    "audio_4.webm"
  ],
  "additional_data": {
    "emr_encounter_id": "enc_123",
    "emr_patient_id": "pat_456"
  },
  "templates": {},
  "transcript": null
}
```

If partial processing occurred before expiry, the response includes available results:

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "session_id": "ses_expired456",
  "status": "expired",
  "created_at": "2025-01-19T10:00:00Z",
  "expired_at": "2025-01-19T11:00:00Z",
  "message": "Session expired during processing",
  "model_used": "pro",
  "language_detected": "en",
  "audio_files_received": 5,
  "audio_files": [
    "audio_0.webm",
    "audio_1.webm",
    "audio_2.webm",
    "audio_3.webm",
    "audio_4.webm"
  ],
  "audio_files_processed": 3,
  "additional_data": {
    "emr_encounter_id": "enc_789"
  },
  "templates": {
    "soap": {
      "status": "success",
      "data": {
        "subjective": "...",
        "objective": "...",
        "assessment": "...",
        "plan": "..."
      }
    },
    "medications": {
      "status": "failed",
      "error": {
        "code": "processing_incomplete",
        "message": "Session expired before extraction could complete"
      }
    }
  },
  "transcript": "Doctor: Good morning...\nPatient: I've been having..."
}
```

### Expired Session Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique session identifier |
| `status` | string | Always `expired` |
| `created_at` | string | ISO 8601 session creation timestamp |
| `expired_at` | string | ISO 8601 expiry timestamp |
| `message` | string | Human-readable expiry reason |
| `audio_files_received` | integer | Total audio files received before expiry |
| `audio_files` | array | List of audio file names received |
| `audio_files_processed` | integer | Files processed before expiry (if processing started) |
| `additional_data` | object | EMR pass-through data (if provided) |
| `templates` | object | Partial extraction results (if processing started) |
| `transcript` | string | Partial transcript (if transcription started) |

---

## 6.6 Additional Data Pass-through

The `additional_data` object is stored with the session and returned in all responses and webhooks. This allows EMR clients to correlate sessions with their internal records.

### Use Cases

```json
{
  "additional_data": {
    "emr_encounter_id": "enc_123",
    "emr_patient_id": "pat_456",
    "department": "cardiology",
    "physician_id": "dr_smith"
  }
}
```

### Requirements

- Scribe Services MUST return `additional_data` unchanged in responses and webhooks
- `additional_data` MUST NOT be used for processing logic
- `additional_data` SHOULD NOT contain PHI (Protected Health Information)
- Maximum `additional_data` size: 4KB recommended

---

## 6.7 Session Lifecycle Summary

| Action | Endpoint | Result |
|--------|----------|--------|
| Create session | `POST /sessions` | Session in `created` state |
| Upload audio | `POST /sessions/{id}/audio` | Session moves to `recording` |
| End session | `POST /sessions/{id}/end` | Session moves to `processing` |
| Check status | `GET /sessions/{id}` | Returns current state and data |
| Timeout | (automatic) | Session moves to `expired` |

---

**Previous:** [Authentication](./05-authentication.md) | **Next:** [Audio Ingestion](./07-audio-ingestion.md)
