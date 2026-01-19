# 8. Templates

**MedScribeAlliance Protocol Specification v0.1**

---

## 8.1 Overview

**Templates** define structured output formats for extracted medical information. EMR clients request specific templates when creating a session, and the Scribe Service returns data in those formats.

```
Audio Input → Transcription → Template Extraction → Structured Output
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
                  SOAP        Medications      Custom
```

---

## 8.2 List Templates

**Endpoint:** `GET /templates`

**Required:** Yes

Returns templates available to the authenticated EMR/user.

### Request

```http
GET /templates HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
```

### Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "templates": [
    {
      "id": "transcript",
      "name": "Full Transcript",
      "description": "Complete voice-to-text transcription"
    },
    {
      "id": "soap",
      "name": "SOAP Note",
      "description": "Standard Subjective, Objective, Assessment, Plan format"
    },
    {
      "id": "medications",
      "name": "Medications List",
      "description": "Extracted medication information"
    },
    {
      "id": "discharge_summary",
      "name": "Discharge Summary",
      "description": "Hospital discharge documentation"
    },
    {
      "id": "referral_letter",
      "name": "Referral Letter",
      "description": "Specialist referral documentation"
    }
  ]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique template identifier for API calls |
| `name` | string | Human-readable template name |
| `description` | string | Brief description of template purpose |

### Authentication Note

The templates endpoint is behind authentication. It returns only templates available to the authenticated EMR or user, which may include:

- Standard templates available to all
- Custom templates created by the EMR
- User-specific templates (in B2C model)

---

## 8.3 Standard Templates

The following template IDs are RECOMMENDED for standardization across implementations:

| Template ID | Description | Always Generated |
|-------------|-------------|------------------|
| `transcript` | Full voice-to-text transcription | Yes (internally) |
| `soap` | SOAP note format | No |
| `medications` | Medication list extraction | No |
| `discharge_summary` | Hospital discharge summary | No |
| `referral_letter` | Specialist referral letter | No |
| `hpi` | History of Present Illness | No |
| `vitals` | Vital signs extraction | No |

### Transcript Requirement

Scribe Services MUST generate a complete transcript for every session internally, regardless of which templates are requested. The transcript is:

- Always generated during processing
- Returned to EMR only if `include_transcript: true` in session creation
- The foundation for all template extractions

---

## 8.4 Requesting Templates

Templates are specified during session creation:

```http
POST /sessions HTTP/1.1
Authorization: X-API-Key sk_live_xxx
Content-Type: application/json

{
  "templates": ["soap", "medications"],
  "include_transcript": true
}
```

### Multiple Templates

EMR clients MAY request multiple templates in a single session:

```json
{
  "templates": ["soap", "medications", "referral_letter"]
}
```

All requested templates are extracted from the same audio/transcript.

---

## 8.5 Template Output Formats

### SOAP Template (`soap`)

```json
{
  "soap": {
    "subjective": "Patient is a 45-year-old male presenting with chest pain for 3 days. Pain is described as pressure-like, radiating to left arm. Worse with exertion, relieved by rest. No associated shortness of breath or diaphoresis. Past medical history includes hypertension and hyperlipidemia.",
    "objective": "Vitals: BP 130/85 mmHg, HR 78 bpm, Temp 98.6°F, SpO2 98% on room air. General: Alert, oriented, mild distress. Cardiovascular: Regular rate and rhythm, no murmurs, rubs, or gallops. Lungs: Clear to auscultation bilaterally. Extremities: No edema.",
    "assessment": "1. Chest pain - suspected stable angina\n2. Hypertension - suboptimally controlled\n3. Hyperlipidemia - on statin therapy",
    "plan": "1. ECG today to evaluate for ischemic changes\n2. Troponin levels to rule out acute coronary syndrome\n3. Lipid panel\n4. Increase lisinopril from 10mg to 20mg daily\n5. Start aspirin 81mg daily\n6. Cardiology referral for stress test\n7. Return in 1 week or sooner if symptoms worsen"
  }
}
```

### Medications Template (`medications`)

```json
{
  "medications": [
    {
      "name": "Lisinopril",
      "dosage": "20mg",
      "frequency": "once daily",
      "route": "oral",
      "instructions": "Take in the morning",
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
```

#### Medication Action Values

| Action | Description |
|--------|-------------|
| `start` | New medication being prescribed |
| `continue` | Existing medication to continue |
| `increase` | Dosage being increased |
| `decrease` | Dosage being decreased |
| `stop` | Medication being discontinued |
| `hold` | Medication temporarily paused |

### Transcript Template (`transcript`)

```json
{
  "transcript": "Doctor: Good morning, what brings you in today?\nPatient: I've been having chest pain for about three days now.\nDoctor: Can you describe the pain? Where exactly do you feel it?\nPatient: It's like a pressure in the center of my chest. Sometimes it goes down my left arm.\nDoctor: Does anything make it better or worse?\nPatient: It gets worse when I walk or climb stairs. Resting helps.\nDoctor: Any shortness of breath or sweating with the pain?\nPatient: No, just the chest discomfort.\nDoctor: Let me check your vitals and do an examination..."
}
```

---

## 8.6 Custom Templates

Scribe Services MAY support custom templates created by EMRs or users. Custom template creation and management interfaces are **outside the scope of this protocol**.

### Requesting Custom Templates

Custom templates are requested the same way as standard templates:

```json
{
  "templates": ["soap", "my_custom_template"]
}
```

### Template Not Found Handling

If a requested template is not available, the Scribe Service MUST:

1. Process all available templates
2. Return results for available templates
3. Include error information for unavailable templates
4. NOT fail the entire extraction

#### Example Response with Unavailable Template

```json
{
  "session_id": "ses_abc123def456",
  "status": "completed",
  "templates": {
    "soap": {
      "subjective": "...",
      "objective": "...",
      "assessment": "...",
      "plan": "..."
    }
  },
  "template_errors": [
    {
      "template_id": "custom_specialty_note",
      "error": "template_not_found",
      "message": "Template 'custom_specialty_note' is not available"
    }
  ]
}
```

---

## 8.7 Template Best Practices

### For EMR Clients

1. **Check available templates** via `GET /templates` before session creation
2. **Request only needed templates** to optimize processing
3. **Handle partial results** when some templates fail
4. **Always request transcript** if raw text is needed for custom processing

### For Scribe Services

1. **Support standard template IDs** for interoperability
2. **Gracefully handle unknown templates** with clear errors
3. **Document custom template creation** (if supported)
4. **Generate transcript internally** for all sessions

---

**Previous:** [Audio Ingestion](./07-audio-ingestion.md) | **Next:** [Extraction](./09-extraction.md)
