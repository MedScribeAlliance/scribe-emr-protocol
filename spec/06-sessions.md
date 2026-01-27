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
Authorization: X-API-Key | sk_live_xxx
Content-Type: application/json

{
  "templates": ["soap", "medications"],
  "model": "pro",
  "language_hint": ["hi"],
  "transcript_language": "en",
  "upload_type": "chunked",
  "additional_data": {
    "emr_encounter_id": "enc_123",
    "emr_patient_id": "pat_456"
  }
}
```
PAYLOAD open API spec
```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "templates",
    "upload_type",
    "communication_protocol"
  ],
  "properties": {
    "templates": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "maxItems": 2,
      "description": "Derived from /templates api response in /.well-known/discovery. See discovery document for validations."
    },
    "model": {
      "type": "string",
      "enum": [
        "pro",
        "lite"
      ],
      "default": "lite"
    },
    "language_hint": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 2
      },
      "description": "IRC language codes. See discovery document for supported languages.",
    },
    "transcript_language": {
      "type": "array",
      "items": {
        "type": "string",
        "maxLength": 2
      },
      "default": [
        "en"
      ],
      "description": "IRC language codes. See discovery document for supported languages."
    },
    "upload_type": {
      "type": "string",
      "enum": [
        "chunked",
        "single",
        "stream"
      ]
    },
    "communication_protocol": {
      "type": "string",
      "enum": [
        "websocket",
        "http",
        "rpc"
      ]
    },
    "additional_data": {
      "type": "object",
      "additionalProperties": true
    }
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
```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "session_id",
    "status",
    "created_at",
    "expires_at",
    "upload_url"
  ],
  "properties": {
    "session_id": {
      "type": "string",
      "minLength": 16,
      "maxLength": 32,
      "pattern": "^ses_[a-zA-Z0-9]+$",
      "description": "Unique identifier for the session (16 or 32 bytes string)",
      "example": "ses_abc123def456"
    },
    "status": {
      "type": "string",
      "enum": [
        "created",
        "initialized",
        "processing",
        "completed",
        "failed"
      ],
      "description": "Current status of the session",
      "example": "created"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when the session was created",
      "example": "2025-01-19T10:30:00Z"
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when the session will expire",
      "example": "2025-01-19T11:30:00Z"
    },
    "upload_url": {
      "type": "string",
      "format": "uri",
      "description": "URL endpoint for uploading audio files to this session",
      "example": "https://api.scribe.example.com/v1/sessions/ses_abc123def456/audio"
    }
  }
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
  "status": "initialized",
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
```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "session_id",
    "status",
    "created_at",
    "expires_at",
    "audio_files_received",
    "audio_files",
    "additional_data",
    "transcript"
  ],
  "properties": {
    "session_id": {
      "type": "string",
      "minLength": 16,
      "maxLength": 32,
      "pattern": "^ses_[a-zA-Z0-9]+$",
      "description": "Unique identifier for the session (16 or 32 bytes string)",
      "example": "ses_abc123def456"
    },
    "status": {
      "type": "string",
      "enum": [
        "created",
        "initialized",
        "processing",
        "completed",
        "failed"
      ],
      "description": "Current status of the session",
      "example": "initialized"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when the session was created",
      "example": "2025-01-19T10:30:00Z"
    },
    "expires_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when the session will expire",
      "example": "2025-01-19T11:30:00Z"
    },
    "audio_files_received": {
      "type": "integer",
      "description": "Number of audio files received",
      "example": 3
    },
    "audio_files": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of audio file names",
      "example": [
        "audio_0.webm",
        "audio_1.webm",
        "audio_2.webm"
      ]
    },
    "additional_data": {
      "type": "object",
      "additionalProperties": true,
      "description": "Pass-through data returned in webhooks and responses",
      "example": {
        "emr_encounter_id": "enc_123"
      }
    },
    "transcript": {
      "type": "string",
      "description": "Transcript of the audio files",
      "example": "Doctor: Good morning...\nPatient: I've been having..."
    }
  }
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
  "templates": [
    "soap": {
      "status": "success",
      "data": {
        "subjective": ,
        "objective": "...",
        "assessment": "...",
        "plan": "..."
      }
    },
    "medications": {
      "status": "success",
      "data": [...]
    }
  ],
  "transcript": "Doctor: ...\nPatient: ..."
}
```

```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "required": [
    "session_id",
    "status",
    "created_at",
    "audio_files_received",
    "audio_files"
  ],
  "properties": {
    "session_id": {
      "type": "string",
      "minLength": 16,
      "maxLength": 32,
      "pattern": "^ses_[a-zA-Z0-9]+$",
      "description": "Unique identifier for the session (16 or 32 bytes string)",
      "example": "ses_abc123def456"
    },
    "status": {
      "type": "string",
      "enum": [
        "created",
        "initialized",
        "processing",
        "completed",
        "failed"
      ],
      "description": "Current status of the session",
      "example": "completed"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when the session was created",
      "example": "2025-01-19T10:30:00Z"
    },
    "completed_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp when the session was completed",
      "example": "2025-01-19T10:35:00Z"
    },
    "model_used": {
      "type": "string",
      "enum": [
        "pro",
        "lite"
      ],
      "description": "The model that was used for processing",
      "example": "pro"
    },
    "language_detected": {
      "type": "string",
      "minLength": 2,
      "maxLength": 2,
      "description": "ISO 639-1 language code detected from the audio",
      "example": "hi"
    },
    "audio_files_received": {
      "type": "integer",
      "minimum": 0,
      "description": "Total number of audio files received by backend",
      "example": 3
    },
    "audio_files": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of audio file names received",
      "example": ["audio_0.webm", "audio_1.webm", "audio_2.webm"]
    },
    "additional_data": {
      "type": "object",
      "additionalProperties": true,
      "description": "Additional data sent by user during session initialization as raw JSON",
      "example": {
        "emr_encounter_id": "enc_123"
      }
    },
    "templates": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "required": [
          "status"
        ],
        "properties": {
          "status": {
            "type": "string",
            "enum": [
              "success",
              "failed",
              "processing"
            ],
            "description": "Processing status of the template"
          },
          "data": {
            "oneOf": [
              {
                "type": "object",
                "additionalProperties": true
              },
              {
                "type": "array",
                "items": {
                  "type": "object",
                  "additionalProperties": true
                }
              }
            ],
            "description": "Template data - could be an object, array of objects, or nested JSON depending on the provider template response"
          },
          "error": {
            "type": "string",
            "description": "Error message if status is failed"
          }
        }
      },
      "description": "Template processing results indexed by template_id",
      "example": {
        "soap": {
          "status": "success",
          "data": {
            "subjective": "Patient reports headache for 3 days",
            "objective": "BP 120/80,Temp 98.6F",
            "assessment": "Tension headache",
            "plan": "Prescribed ibuprofen 400mg"
          }
        },
        "medications": {
          "status": "success",
          "data": [
            {
              "name": "Ibuprofen",
              "dosage": "400mg",
              "frequency": "twice daily"
            }
          ]
        }
      }
    },
    "transcript": {
      "type": "string",
      "description": "Full transcript of the audio conversation",
      "example": "Doctor: Good morning, how are you feeling today?\nPatient: I've been having headaches..."
    }
  }
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
  "templates": [
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
  ],
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
```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Session Partial Processing Response",
  "type": "object",
  "required": [
    "session_id",
    "status",
    "created_at",
    "audio_files_received",
    "audio_files",
    "audio_files_processed",
    "templates"
  ],
  "properties": {
    "session_id": {
      "type": "string",
      "minLength": 16,
      "maxLength": 32,
      "pattern": "^ses_[a-zA-Z0-9]+$",
      "description": "Unique identifier for the session",
      "example": "ses_abc123def456"
    },

    "status": {
      "type": "string",
      "enum": ["created", "processing", "partial", "completed", "failed"],
      "description": "Overall processing state of the session",
      "example": "partial"
    },

    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 timestamp when the session was created",
      "example": "2025-01-19T10:30:00Z"
    },

    "completed_at": {
      "type": ["string", "null"],
      "format": "date-time",
      "description": "Timestamp when processing completed (may be null for partial)",
      "example": "2025-01-19T10:35:00Z"
    },

    "model_used": {
      "type": "string",
      "enum": ["pro", "lite"],
      "description": "Model used to process the audio",
      "example": "pro"
    },

    "language_detected": {
      "type": "string",
      "minLength": 2,
      "maxLength": 5,
      "description": "Detected language code (ISO 639-1 or 639-3)",
      "example": "hi"
    },

    "audio_files_received": {
      "type": "integer",
      "minimum": 0,
      "description": "Total audio files received",
      "example": 3
    },

    "audio_files_processed": {
      "type": "integer",
      "minimum": 0,
      "description": "Number of audio files successfully processed",
      "example": 2
    },

    "audio_files": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of uploaded audio files",
      "example": ["audio_0.webm", "audio_1.webm", "audio_2.webm"]
    },

    "additional_data": {
      "type": "object",
      "additionalProperties": true,
      "description": "Arbitrary metadata provided by the client",
      "example": {
        "emr_encounter_id": "enc_123"
      }
    },

    "templates": {
      "type": "object",
      "description": "Per-template extraction status and results",
      "additionalProperties": {
        "type": "object",
        "required": ["status"],
        "properties": {
          "status": {
            "type": "string",
            "enum": ["success", "failed", "processing"],
            "description": "Template processing state"
          },

          "data": {
            "oneOf": [
              {
                "type": "object",
                "additionalProperties": true
              },
              {
                "type": "array",
                "items": {
                  "type": "object",
                  "additionalProperties": true
                }
              }
            ],
            "description": "Extracted structured data if successful"
          },

          "error": {
            "type": "object",
            "required": ["code", "message"],
            "properties": {
              "code": {
                "type": "string",
                "description": "Machine-readable error code",
                "example": "extraction_failed"
              },
              "message": {
                "type": "string",
                "description": "Human-readable error description",
                "example": "Could not extract medication information from audio"
              }
            }
          }
        }
      }
    },

    "transcript": {
      "type": "string",
      "description": "Partial or full transcript of the audio session",
      "example": "Doctor: ...\nPatient: ..."
    },

    "processing_errors": {
      "type": "array",
      "description": "Non-fatal processing issues",
      "items": {
        "type": "object",
        "required": ["type", "message"],
        "properties": {
          "type": {
            "type": "string",
            "description": "Category of the processing error",
            "example": "audio_file_skipped"
          },
          "message": {
            "type": "string",
            "description": "Description of the issue",
            "example": "Audio file audio_2.webm skipped due to poor quality"
          },
          "file": {
            "type": "string",
            "description": "Associated file (if applicable)",
            "example": "audio_2.webm"
          }
        }
      }
    }
  }
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

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "End Session Response",
  "type": "object",
  "required": [
    "session_id",
    "status",
    "message",
    "audio_files_received",
    "audio_files"
  ],
  "properties": {
    "session_id": {
      "type": "string",
      "minLength": 16,
      "maxLength": 32,
      "pattern": "^ses_[a-zA-Z0-9]+$",
      "description": "Unique identifier for the session",
      "example": "ses_abc123def456"
    },

    "status": {
      "type": "string",
      "enum": ["processing"],
      "description": "Session status after ending",
      "example": "processing"
    },

    "message": {
      "type": "string",
      "description": "Human-readable status message",
      "example": "Session ended. Processing started."
    },

    "audio_files_received": {
      "type": "integer",
      "minimum": 0,
      "description": "Total number of audio files successfully received",
      "example": 3
    },

    "audio_files": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of audio file names received for this session",
      "example": [
        "chunk_0.webm",
        "chunk_1.webm",
        "chunk_2.webm"
      ]
    }
  }
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
```
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Expired Session Response",
  "type": "object",
  "required": [
    "session_id",
    "status",
    "created_at",
    "expired_at",
    "message",
    "audio_files_received",
    "audio_files"
  ],
  "properties": {
    "session_id": {
      "type": "string",
      "minLength": 16,
      "maxLength": 32,
      "pattern": "^ses_[a-zA-Z0-9]+$",
      "description": "Unique identifier for the session",
      "example": "ses_expired123"
    },

    "status": {
      "type": "string",
      "enum": ["expired"],
      "description": "Session status after expiration",
      "example": "expired"
    },

    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 timestamp when the session was created",
      "example": "2025-01-19T10:00:00Z"
    },

    "expired_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO-8601 timestamp when the session expired",
      "example": "2025-01-19T11:00:00Z"
    },

    "message": {
      "type": "string",
      "description": "Human-readable status message",
      "example": "Session expired before processing was initiated"
    },

    "audio_files_received": {
      "type": "integer",
      "minimum": 0,
      "description": "Total number of audio files successfully received",
      "example": 5
    },

    "audio_files": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "List of audio file names received for this session",
      "example": [
        "audio_0.webm",
        "audio_1.webm",
        "audio_2.webm",
        "audio_3.webm",
        "audio_4.webm"
      ]
    }
  }
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
