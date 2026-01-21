# 9. Extraction & Response

**MedScribeAlliance Protocol Specification v0.1**

---

## 9.1 Overview

After a session is ended, the Scribe Service processes the audio and extracts structured data based on requested templates. Results are delivered via:

1. **Webhook** - Proactive push to EMR (recommended)
2. **Polling** - EMR fetches via `GET /sessions/{id}`
3. **Client SDK** - Browser postMessage/callback

---

## 9.2 Response Structure

All extraction responses follow this structure:

```json
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
    "emr_encounter_id": "enc_123",
    "emr_patient_id": "pat_456"
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
      "data": [
        {
          "name": "Aspirin",
          "dosage": "81mg",
          "frequency": "once daily"
        }
      ]
    }
  },
  "transcript": "Doctor: Good morning...\nPatient: I've been having..."
}
```

---

## 9.3 Response Fields

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `session_id` | string | Unique session identifier |
| `status` | string | Session status (`completed`, `partial`, `failed`) |
| `created_at` | string | ISO 8601 session creation timestamp |
| `model_used` | string | Model ID used for processing |
| `language_detected` | string | ISO 639-1 detected language code |
| `audio_files_received` | integer | Total number of audio files received |
| `audio_files` | array | List of audio file names received |

### Conditional Fields

| Field | Type | Condition | Description |
|-------|------|-----------|-------------|
| `completed_at` | string | If `status` = `completed` or `partial` | ISO 8601 completion timestamp |
| `additional_data` | object | If provided at creation | EMR pass-through data |
| `templates` | object | If `status` = `completed` or `partial` | Extracted template data with per-template status |
| `transcript` | string | If `status` = `completed` or `partial` | Full transcription |
| `audio_files_processed` | integer | If `status` = `partial` | Number of audio files successfully processed |
| `processing_errors` | array | If `status` = `partial` | Session-level processing errors |

### Error Fields (for failed sessions)

| Field | Type | Description |
|-------|------|-------------|
| `error.code` | string | Error code |
| `error.message` | string | Human-readable error message |

---

## 9.4 Template Output

The `templates` object contains extracted data keyed by template ID. Each template entry includes a `status` field indicating success or failure, with either `data` or `error` accordingly:

### Template Entry Structure

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `success` or `failed` |
| `data` | object/array | Template output (present if `status` = `success`) |
| `error` | object | Error details (present if `status` = `failed`) |
| `error.code` | string | Error code |
| `error.message` | string | Human-readable error message |

### Example: All Templates Successful

```json
{
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
  }
}
```

### Example: Mixed Success and Failure

```json
{
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
  }
}
```

Each template's `data` structure is defined by the template type. See [Templates](./08-templates.md) for format details.

---

## 9.5 Transcript Format

The full transcript is always included in completed session responses:

```json
{
  "transcript": "Doctor: Good morning, what brings you in today?\nPatient: I've been having chest pain for about three days now.\nDoctor: Can you describe the pain?\nPatient: It's like a pressure in my chest..."
}
```

### Speaker Labels

Transcripts SHOULD include speaker labels when speaker diarization is available:

```
Doctor: [utterance]
Patient: [utterance]
```

If speaker identification is not available, plain text is acceptable:

```
Good morning, what brings you in today? I've been having chest pain...
```

---

## 9.6 Template Error Codes

When a template extraction fails, the error is included within that template's entry:

### Error Codes

| Code | Description |
|------|-------------|
| `template_not_found` | Requested template does not exist |
| `extraction_failed` | Template exists but extraction failed |
| `insufficient_audio` | Not enough audio for meaningful extraction |
| `timeout` | Template extraction timed out |

### Example: Partial Response with Template Errors

```json
{
  "session_id": "ses_abc123def456",
  "status": "partial",
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
    "custom_cardio_note": {
      "status": "failed",
      "error": {
        "code": "template_not_found",
        "message": "Template 'custom_cardio_note' is not available"
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
  "transcript": "Doctor: Good morning..."
}
```

---

## 9.7 Failed Sessions

When processing fails entirely:

```json
{
  "session_id": "ses_abc123def456",
  "status": "failed",
  "created_at": "2025-01-19T10:30:00Z",
  "model_used": "pro",
  "audio_files_received": 3,
  "audio_files": ["audio_0.webm", "audio_1.webm", "audio_2.webm"],
  "additional_data": {
    "emr_encounter_id": "enc_123"
  },
  "error": {
    "code": "processing_failed",
    "message": "Unable to process audio due to poor quality"
  }
}
```

### Common Failure Reasons

| Code | Description |
|------|-------------|
| `processing_failed` | General processing failure |
| `audio_quality_poor` | Audio too noisy or unclear |
| `audio_too_short` | Insufficient audio for processing |
| `language_unsupported` | Detected language not supported |
| `internal_error` | Internal service error |

---

## 9.8 Polling for Results

EMR clients can poll for results using `GET /sessions/{id}`:

```http
GET /sessions/ses_abc123def456 HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
```

### Polling Strategy

```
┌─────────────┐
│  End Session│
└──────┬──────┘
       │
       ▼
┌─────────────┐     status = processing
│   Poll      │◀────────────────────────┐
└──────┬──────┘                         │
       │                                │
       ▼                                │
   ┌───────┐                            │
   │Status?│────────────────────────────┘
   └───┬───┘
       │ status = completed/failed
       ▼
┌─────────────┐
│Process Data │
└─────────────┘
```

### Recommended Polling Intervals

| Elapsed Time | Interval |
|--------------|----------|
| 0-30 seconds | 2 seconds |
| 30-60 seconds | 5 seconds |
| 60+ seconds | 10 seconds |

### Polling vs Webhooks

| Aspect | Polling | Webhooks |
|--------|---------|----------|
| Latency | Higher (interval-based) | Lower (immediate) |
| Complexity | Lower | Higher |
| Reliability | Self-managed | Requires retry handling |
| Resource usage | Higher | Lower |

**Recommendation:** Use webhooks when possible; fall back to polling if webhooks fail.

---

## 9.9 Example Complete Response

```json
{
  "session_id": "ses_abc123def456",
  "status": "completed",
  "created_at": "2025-01-19T10:30:00Z",
  "completed_at": "2025-01-19T10:35:12Z",
  "model_used": "pro",
  "language_detected": "en",
  "audio_files_received": 4,
  "audio_files": ["audio_0.webm", "audio_1.webm", "audio_2.webm", "audio_3.webm"],
  "additional_data": {
    "emr_encounter_id": "enc_789",
    "emr_patient_id": "pat_123",
    "department": "internal_medicine"
  },
  "templates": {
    "soap": {
      "status": "success",
      "data": {
        "subjective": "45-year-old male presents with chest pain for 3 days. Describes pressure-like sensation in center of chest, radiating to left arm. Worse with exertion, relieved by rest. Denies shortness of breath, diaphoresis, or palpitations. PMH significant for HTN and HLD.",
        "objective": "VS: BP 130/85, HR 78, RR 16, Temp 98.6°F, SpO2 98% RA. General: Alert, oriented, NAD. CV: RRR, no m/r/g. Lungs: CTAB. Ext: No edema.",
        "assessment": "1. Chest pain - concerning for stable angina given exertional component and risk factors\n2. Hypertension - suboptimally controlled\n3. Hyperlipidemia - on statin",
        "plan": "1. ECG today\n2. Troponin x2\n3. Lipid panel\n4. Increase lisinopril 10mg → 20mg daily\n5. Start ASA 81mg daily\n6. Cardiology referral for stress test\n7. RTC 1 week"
      }
    },
    "medications": {
      "status": "success",
      "data": [
        {
          "name": "Lisinopril",
          "dosage": "20mg",
          "frequency": "once daily",
          "route": "oral",
          "instructions": "Take in morning",
          "action": "increase"
        },
        {
          "name": "Aspirin",
          "dosage": "81mg",
          "frequency": "once daily",
          "route": "oral",
          "instructions": "Take with food",
          "action": "start"
        },
        {
          "name": "Atorvastatin",
          "dosage": "40mg",
          "frequency": "once daily",
          "route": "oral",
          "instructions": "Take at bedtime",
          "action": "continue"
        }
      ]
    }
  },
  "transcript": "Doctor: Good morning Mr. Johnson, what brings you in today?\n\nPatient: Hi doctor. I've been having this chest pain for about three days now.\n\nDoctor: Tell me more about the pain. Where exactly do you feel it?\n\nPatient: It's right here in the center of my chest. Sometimes it goes down my left arm too.\n\nDoctor: What does the pain feel like? Is it sharp, dull, pressure-like?\n\nPatient: It's more like pressure. Like someone is sitting on my chest.\n\nDoctor: What makes it better or worse?\n\nPatient: Walking or climbing stairs makes it worse. When I rest, it goes away after a few minutes.\n\nDoctor: Any shortness of breath, sweating, or heart racing with the pain?\n\nPatient: No, none of that. Just the chest pressure.\n\nDoctor: Okay, let me examine you. Your blood pressure is 130 over 85, heart rate 78. Let me listen to your heart and lungs..."
}
```

---

## 9.10 Example Partial Response

```json
{
  "session_id": "ses_abc123def456",
  "status": "partial",
  "created_at": "2025-01-19T10:30:00Z",
  "completed_at": "2025-01-19T10:35:12Z",
  "model_used": "pro",
  "language_detected": "en",
  "audio_files_received": 4,
  "audio_files": ["audio_0.webm", "audio_1.webm", "audio_2.webm", "audio_3.webm"],
  "audio_files_processed": 3,
  "additional_data": {
    "emr_encounter_id": "enc_789",
    "emr_patient_id": "pat_123",
    "department": "internal_medicine"
  },
  "templates": {
    "soap": {
      "status": "success",
      "data": {
        "subjective": "45-year-old male presents with chest pain for 3 days...",
        "objective": "VS: BP 130/85, HR 78...",
        "assessment": "1. Chest pain - concerning for stable angina...",
        "plan": "1. ECG today\n2. Troponin x2..."
      }
    },
    "medications": {
      "status": "failed",
      "error": {
        "code": "extraction_failed",
        "message": "Could not extract medication information due to audio quality issues in relevant segment"
      }
    }
  },
  "transcript": "Doctor: Good morning Mr. Johnson...\n[audio_3.webm unavailable due to audio quality]",
  "processing_errors": [
    {
      "type": "audio_file_skipped",
      "message": "Audio file audio_3.webm skipped due to poor quality",
      "file": "audio_3.webm"
    }
  ]
}
```

---

**Previous:** [Templates](./08-templates.md) | **Next:** [Webhooks](./10-webhooks.md)
