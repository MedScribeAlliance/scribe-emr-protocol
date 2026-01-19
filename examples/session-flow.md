# Session Flow Example

This document walks through a complete session flow from discovery to extraction.

## Prerequisites

- Scribe Service URL: `https://api.scribe.example.com`
- API Key: `sk_live_xxx` (for B2B integration)

---

## Step 1: Discover Capabilities

```bash
curl -s https://scribe.example.com/.well-known/medscribealliance | jq
```

**Response:**
```json
{
  "protocol": "medscribealliance",
  "protocol_version": "0.1",
  "capabilities": {
    "audio_formats": ["audio/webm;codecs=opus", "audio/wav"],
    "max_chunk_duration_seconds": 20
  },
  "models": [
    {
      "id": "pro",
      "languages": ["en", "hi", "ta"]
    }
  ]
}
```

---

## Step 2: Register Webhook (One-time)

```bash
curl -X POST https://api.scribe.example.com/v1/webhooks \
  -H "X-API-Key: sk_live_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://emr.example.com/scribe-webhook",
    "events": ["session.completed", "session.failed"],
    "secret": "whsec_my_secret_key"
  }'
```

**Response:**
```json
{
  "webhook_id": "wh_abc123",
  "status": "active"
}
```

---

## Step 3: Create Session

```bash
curl -X POST https://api.scribe.example.com/v1/sessions \
  -H "X-API-Key: sk_live_xxx" \
  -H "Content-Type: application/json" \
  -d '{
    "templates": ["soap", "medications"],
    "model": "pro",
    "language_hint": "en",
    "include_transcript": true,
    "metadata": {
      "emr_encounter_id": "enc_12345",
      "emr_patient_id": "pat_67890"
    }
  }'
```

**Response:**
```json
{
  "session_id": "ses_abc123def456",
  "status": "created",
  "created_at": "2025-01-19T10:30:00Z",
  "expires_at": "2025-01-19T11:30:00Z"
}
```

---

## Step 4: Upload Audio Chunks

### Chunk 1 (0-15 seconds)

```bash
curl -X POST https://api.scribe.example.com/v1/sessions/ses_abc123def456/audio \
  -H "X-API-Key: sk_live_xxx" \
  -H "Content-Type: audio/webm;codecs=opus" \
  -H "X-Chunk-Index: 0" \
  --data-binary @chunk_0.webm
```

**Response:**
```json
{
  "session_id": "ses_abc123def456",
  "chunk_index": 0,
  "chunk_duration_ms": 15000,
  "total_duration_ms": 15000,
  "status": "received"
}
```

### Chunk 2 (15-30 seconds)

```bash
curl -X POST https://api.scribe.example.com/v1/sessions/ses_abc123def456/audio \
  -H "X-API-Key: sk_live_xxx" \
  -H "Content-Type: audio/webm;codecs=opus" \
  -H "X-Chunk-Index: 1" \
  --data-binary @chunk_1.webm
```

**Response:**
```json
{
  "session_id": "ses_abc123def456",
  "chunk_index": 1,
  "chunk_duration_ms": 15000,
  "total_duration_ms": 30000,
  "status": "received"
}
```

### Continue uploading chunks...

---

## Step 5: End Session

```bash
curl -X POST https://api.scribe.example.com/v1/sessions/ses_abc123def456/end \
  -H "X-API-Key: sk_live_xxx"
```

**Response:**
```json
{
  "session_id": "ses_abc123def456",
  "status": "processing",
  "audio_duration_ms": 180000
}
```

---

## Step 6: Receive Webhook

The Scribe Service sends a POST to your webhook URL:

```http
POST /scribe-webhook HTTP/1.1
Host: emr.example.com
Content-Type: application/json
X-MSA-Signature: t=1705661700,v1=a2b3c4d5e6f7...

{
  "event": "session.completed",
  "timestamp": "2025-01-19T10:35:00Z",
  "data": {
    "session_id": "ses_abc123def456",
    "status": "completed",
    "templates": {
      "soap": {
        "subjective": "Patient presents with...",
        "objective": "VS: BP 130/85...",
        "assessment": "1. Chest pain...",
        "plan": "1. ECG today..."
      },
      "medications": [
        {
          "name": "Aspirin",
          "dosage": "81mg",
          "action": "start"
        }
      ]
    },
    "transcript": "Doctor: Good morning...",
    "metadata": {
      "emr_encounter_id": "enc_12345",
      "emr_patient_id": "pat_67890"
    }
  }
}
```

---

## Step 7: Verify Webhook Signature

```python
import hmac
import hashlib

def verify_signature(payload, signature_header, secret):
    parts = dict(p.split('=') for p in signature_header.split(','))
    timestamp = parts['t']
    signature = parts['v1']
    
    signed_payload = f"{timestamp}.{payload}"
    expected = hmac.new(
        secret.encode(),
        signed_payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)

# Verify before processing
if verify_signature(request.body, request.headers['X-MSA-Signature'], 'whsec_my_secret_key'):
    process_extraction(request.json()['data'])
else:
    return 401, "Invalid signature"
```

---

## Alternative: Polling for Results

If webhooks are not configured, poll for results:

```bash
# Poll every 5 seconds
while true; do
  RESPONSE=$(curl -s https://api.scribe.example.com/v1/sessions/ses_abc123def456 \
    -H "X-API-Key: sk_live_xxx")
  
  STATUS=$(echo $RESPONSE | jq -r '.status')
  
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    echo $RESPONSE | jq
    break
  fi
  
  sleep 5
done
```

---

## Error Handling Example

### Session Expired

```bash
curl -X POST https://api.scribe.example.com/v1/sessions/ses_expired/audio \
  -H "X-API-Key: sk_live_xxx" \
  -H "Content-Type: audio/wav" \
  --data-binary @audio.wav
```

**Response:**
```json
{
  "error": {
    "code": "session_expired",
    "message": "Session 'ses_expired' has expired",
    "details": {
      "expired_at": "2025-01-19T11:30:00Z"
    }
  }
}
```

**Action:** Create a new session and re-upload audio.

---

## Complete Flow Diagram

```
EMR Client                           Scribe Service
    │                                      │
    │  GET /.well-known/medscribealliance  │
    │─────────────────────────────────────▶│
    │◀─────────────────────────────────────│
    │         Discovery Document           │
    │                                      │
    │  POST /webhooks (one-time)           │
    │─────────────────────────────────────▶│
    │◀─────────────────────────────────────│
    │         webhook_id                   │
    │                                      │
    │  POST /sessions                      │
    │─────────────────────────────────────▶│
    │◀─────────────────────────────────────│
    │         session_id                   │
    │                                      │
    │  POST /sessions/{id}/audio (chunk 0) │
    │─────────────────────────────────────▶│
    │◀─────────────────────────────────────│
    │                                      │
    │  POST /sessions/{id}/audio (chunk 1) │
    │─────────────────────────────────────▶│
    │◀─────────────────────────────────────│
    │                                      │
    │  POST /sessions/{id}/end             │
    │─────────────────────────────────────▶│
    │◀─────────────────────────────────────│
    │         processing                   │
    │                                      │
    │                    ┌─────────────────┤
    │                    │   Processing    │
    │                    └─────────────────┤
    │                                      │
    │◀─────────────────────────────────────│
    │    Webhook: session.completed        │
    │    {templates, transcript}           │
    │                                      │
```
