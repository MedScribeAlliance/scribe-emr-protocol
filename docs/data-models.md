# SEP Data Models

This document defines the core JSON structures used in the SEP protocol.

## 1. Schema: `Template`

Represents a specific documentation format or "tool" offered by the Scribe.

```json
{
  "id": "soap_note_v1",
  "name": "SOAP Note (Standard)",
  "description": "Standard Subjective, Objective, Assessment, Plan format.",
  "capabilities": ["clinical_notes", "icd10_coding"],
  "input_schema": {
    "type": "object",
    "properties": {
      "specialty": { "type": "string", "enum": ["general", "cardiology"] }
    }
  }
}
```

## 2. Schema: `ContextPayload`

Metadata accompanying the audio. Providing rich context improves transcription accuracy.

```json
{
  "patient": {
    "id": "pat_12345",
    "name": "John Doe",
    "dob": "1980-01-01",
    "gender": "male"
  },
  "encounter": {
    "id": "enc_98765",
    "date": "2023-10-27T10:30:00Z",
    "type": "outpatient",
    "facility": "Main Street Clinic"
  },
  "provider": {
    "id": "prov_555",
    "name": "Dr. Smith"
  }
}
```

## 3. Schema: `ScribeRequest`

The payload for initiating a transcription job (Sync or Async).

```json
{
  "template_id": "soap_note_v1",
  "audio_config": {
    "format": "mp3",
    "sample_rate": 44100,
    "channel_count": 1,
    "language_code": "en-US"
  },
  "context": { ...ContextPayload... },
  "config": {
    "webhook_url": "https://emr-system.com/webhooks/scribe-result",
    "return_fhir": true,
    "return_transcription": true
  }
}
```

## 4. Schema: `ScribeResponse` & `JobResult`

The output returned to the EMR.

```json
{
  "job_id": "job_abc123",
  "status": "completed",
  "created_at": "2023-10-27T10:30:05Z",
  "completed_at": "2023-10-27T10:31:00Z",
  "output": {
    "transcription": "Patient presents with...",
    "structured_data": {
      "soap": {
        "subjective": "...",
        "objective": "...",
        "assessment": "...",
        "plan": "..."
      }
    },
    "fhir_bundles": [
      {
        "resourceType": "Bundle",
        "type": "document",
        "entry": [ ... ]
      }
    ]
  }
}
```

## 5. Schema: `Error`

Standard error format.

```json
{
  "code": "invalid_template",
  "message": "The template 'cardio_v3' does not exist.",
  "request_id": "req_xyz789"
}
```
