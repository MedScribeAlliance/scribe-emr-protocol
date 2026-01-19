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
         │        ┌────────┴────────┐
         │        │                 │
         │        ▼                 ▼
         │  ┌───────────┐    ┌───────────┐
         │  │           │    │           │
         │  │ COMPLETED │    │  FAILED   │
         │  │           │    │           │
         │  └───────────┘    └───────────┘
         │
         ▼
   ┌───────────┐
   │           │
   │  EXPIRED  │
   │           │
   └───────────┘
```

| State | Description |
|-------|-------------|
| `created` | Session created, awaiting audio upload |
| `recording` | Audio upload in progress |
| `processing` | Session ended, extraction in progress |
| `completed` | Extraction complete, results available |
| `failed` | Processing failed |
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
  "include_transcript": true,
  "metadata": {
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
| `language_hint` | string | No | ISO 639-1 language hint. Auto-detected if not provided |
| `include_transcript` | boolean | No | Include full transcript in response. Default: `false` |
| `metadata` | object | No | Pass-through data returned in webhooks and responses |

### Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "created",
  "created_at": "2025-01-19T10:30:00Z",
  "expires_at": "2025-01-19T11:30:00Z",
  "upload_url": "/sessions/ses_abc123def456/audio"
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique session identifier |
| `status` | string | Current session state |
| `created_at` | string | ISO 8601 creation timestamp |
| `expires_at` | string | ISO 8601 expiry timestamp |
| `upload_url` | string | Relative URL for audio upload |

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
HTTP/1.1 200 OK
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "processing",
  "created_at": "2025-01-19T10:30:00Z",
  "expires_at": "2025-01-19T11:30:00Z",
  "audio_duration_ms": 180000,
  "metadata": {
    "emr_encounter_id": "enc_123"
  }
}
```

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
  "audio_duration_ms": 180000,
  "metadata": {
    "emr_encounter_id": "enc_123"
  },
  "templates": {
    "soap": {
      "subjective": "...",
      "objective": "...",
      "assessment": "...",
      "plan": "..."
    },
    "medications": [...]
  },
  "transcript": "Doctor: ...\nPatient: ...",
  "template_errors": []
}
```

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
HTTP/1.1 200 OK
Content-Type: application/json

{
  "session_id": "ses_abc123def456",
  "status": "processing",
  "message": "Session ended. Processing started.",
  "audio_duration_ms": 180000
}
```

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

```http
GET /sessions/ses_expired123
```

```http
HTTP/1.1 410 Gone
Content-Type: application/json

{
  "error": {
    "code": "session_expired",
    "message": "Session 'ses_expired123' has expired",
    "details": {
      "session_id": "ses_expired123",
      "expired_at": "2025-01-19T11:00:00Z"
    }
  }
}
```

---

## 6.6 Metadata Pass-through

The `metadata` object is stored with the session and returned in all responses and webhooks. This allows EMR clients to correlate sessions with their internal records.

### Use Cases

```json
{
  "metadata": {
    "emr_encounter_id": "enc_123",
    "emr_patient_id": "pat_456",
    "department": "cardiology",
    "physician_id": "dr_smith"
  }
}
```

### Requirements

- Scribe Services MUST return metadata unchanged in responses and webhooks
- Metadata MUST NOT be used for processing logic
- Metadata SHOULD NOT contain PHI (Protected Health Information)
- Maximum metadata size: 4KB recommended

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
