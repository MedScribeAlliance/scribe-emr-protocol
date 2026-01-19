# 10. Webhooks

**MedScribeAlliance Protocol Specification v0.1**

---

## 10.1 Overview

Webhooks enable proactive delivery of session events and extraction results to EMR clients. This eliminates the need for polling and reduces latency.

```
┌─────────────────┐                    ┌─────────────────┐
│                 │                    │                 │
│  Scribe Service │───── Webhook ─────▶│   EMR Backend   │
│                 │                    │                 │
└─────────────────┘                    └─────────────────┘
```

---

## 10.2 Webhook Registration

**Endpoint:** `POST /webhooks`

**Required:** RECOMMENDED

Registers a webhook endpoint to receive session events.

### Request

```http
POST /webhooks HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: application/json

{
  "url": "https://emr.example.com/scribe-webhook",
  "events": [
    "session.started",
    "session.ended",
    "session.completed",
    "session.failed",
    "session.expired"
  ],
  "secret": "whsec_your_secret_key_here"
}
```

### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | HTTPS webhook endpoint URL |
| `events` | array | Yes | Events to subscribe to |
| `secret` | string | Yes | Secret for signature verification (provided by EMR) |

### Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "webhook_id": "wh_xyz789abc",
  "url": "https://emr.example.com/scribe-webhook",
  "events": [
    "session.started",
    "session.ended", 
    "session.completed",
    "session.failed",
    "session.expired"
  ],
  "status": "active",
  "created_at": "2025-01-19T10:00:00Z"
}
```

### Webhook URL Requirements

- MUST be HTTPS (TLS 1.2+)
- MUST be publicly accessible
- SHOULD respond within 30 seconds
- SHOULD return 2xx status on success

---

## 10.3 Webhook Management

### List Webhooks

```http
GET /webhooks HTTP/1.1
Authorization: X-API-Key sk_live_xxx
```

```json
{
  "webhooks": [
    {
      "webhook_id": "wh_xyz789abc",
      "url": "https://emr.example.com/scribe-webhook",
      "events": ["session.completed", "session.failed"],
      "status": "active",
      "created_at": "2025-01-19T10:00:00Z"
    }
  ]
}
```

### Delete Webhook

```http
DELETE /webhooks/wh_xyz789abc HTTP/1.1
Authorization: X-API-Key sk_live_xxx
```

```http
HTTP/1.1 204 No Content
```

---

## 10.4 Webhook Events

| Event | Description | When Triggered |
|-------|-------------|----------------|
| `session.started` | Session created and ready | After `POST /sessions` |
| `session.ended` | Session ended, processing starting | After `POST /sessions/{id}/end` |
| `session.completed` | Extraction complete | After successful processing |
| `session.failed` | Processing failed | After processing failure |
| `session.expired` | Session timed out | After session timeout |

---

## 10.5 Webhook Payload Structure

All webhook payloads follow this structure:

```json
{
  "event": "event.type",
  "timestamp": "2025-01-19T10:35:00Z",
  "data": {
    // Event-specific data
  }
}
```

### session.started

```json
{
  "event": "session.started",
  "timestamp": "2025-01-19T10:30:00Z",
  "data": {
    "session_id": "ses_abc123def456",
    "status": "created",
    "created_at": "2025-01-19T10:30:00Z",
    "expires_at": "2025-01-19T11:30:00Z",
    "metadata": {
      "emr_encounter_id": "enc_123"
    }
  }
}
```

### session.ended

```json
{
  "event": "session.ended",
  "timestamp": "2025-01-19T10:32:00Z",
  "data": {
    "session_id": "ses_abc123def456",
    "status": "processing",
    "audio_duration_ms": 180000,
    "metadata": {
      "emr_encounter_id": "enc_123"
    }
  }
}
```

### session.completed

```json
{
  "event": "session.completed",
  "timestamp": "2025-01-19T10:35:00Z",
  "data": {
    "session_id": "ses_abc123def456",
    "status": "completed",
    "created_at": "2025-01-19T10:30:00Z",
    "completed_at": "2025-01-19T10:35:00Z",
    "model_used": "pro",
    "language_detected": "hi",
    "audio_duration_ms": 180000,
    "metadata": {
      "emr_encounter_id": "enc_123",
      "emr_patient_id": "pat_456"
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
}
```

### session.failed

```json
{
  "event": "session.failed",
  "timestamp": "2025-01-19T10:35:00Z",
  "data": {
    "session_id": "ses_abc123def456",
    "status": "failed",
    "created_at": "2025-01-19T10:30:00Z",
    "audio_duration_ms": 180000,
    "error": {
      "code": "processing_failed",
      "message": "Unable to process audio due to poor quality"
    },
    "metadata": {
      "emr_encounter_id": "enc_123"
    }
  }
}
```

### session.expired

```json
{
  "event": "session.expired",
  "timestamp": "2025-01-19T11:30:00Z",
  "data": {
    "session_id": "ses_abc123def456",
    "status": "expired",
    "created_at": "2025-01-19T10:30:00Z",
    "expired_at": "2025-01-19T11:30:00Z",
    "message": "Session expired due to inactivity",
    "metadata": {
      "emr_encounter_id": "enc_123"
    }
  }
}
```

---

## 10.6 Signature Verification

Scribe Services MUST sign webhook payloads. EMR Clients MUST verify signatures before processing.

### Signature Header

```http
POST /scribe-webhook HTTP/1.1
Host: emr.example.com
Content-Type: application/json
X-MSA-Signature: t=1705661400,v1=5257a869e7ecebeda32affa62cdca3fa51cded5fa20f8de7...

{...payload...}
```

### Signature Format

```
X-MSA-Signature: t={timestamp},v1={signature}
```

| Component | Description |
|-----------|-------------|
| `t` | Unix timestamp when signature was generated |
| `v1` | HMAC-SHA256 signature (hex encoded) |

### Signature Computation

The signature is computed as:

```
signed_payload = "{timestamp}.{raw_request_body}"
signature = HMAC-SHA256(secret, signed_payload)
```

### Verification Steps

1. Extract `t` (timestamp) and `v1` (signature) from header
2. Verify timestamp is within acceptable window (recommended: 5 minutes)
3. Construct signed payload: `{timestamp}.{raw_body}`
4. Compute HMAC-SHA256 using webhook secret
5. Compare computed signature with `v1` using constant-time comparison
6. Reject request if signature doesn't match

### Python Example

```python
import hmac
import hashlib
import time

def verify_webhook_signature(
    payload: bytes,
    signature_header: str,
    secret: str,
    tolerance_seconds: int = 300
) -> bool:
    """
    Verify webhook signature.
    
    Args:
        payload: Raw request body bytes
        signature_header: X-MSA-Signature header value
        secret: Webhook secret
        tolerance_seconds: Maximum age of signature (default 5 minutes)
    
    Returns:
        True if signature is valid
    """
    # Parse header
    parts = {}
    for item in signature_header.split(','):
        key, value = item.split('=', 1)
        parts[key] = value
    
    timestamp = parts.get('t')
    signature = parts.get('v1')
    
    if not timestamp or not signature:
        return False
    
    # Check timestamp freshness
    try:
        ts = int(timestamp)
        if abs(time.time() - ts) > tolerance_seconds:
            return False
    except ValueError:
        return False
    
    # Compute expected signature
    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    expected = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Constant-time comparison
    return hmac.compare_digest(expected, signature)
```

### Node.js Example

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(payload, signatureHeader, secret) {
  const parts = Object.fromEntries(
    signatureHeader.split(',').map(p => p.split('='))
  );
  
  const timestamp = parts.t;
  const signature = parts.v1;
  
  // Check timestamp (5 minute tolerance)
  const age = Math.abs(Date.now() / 1000 - parseInt(timestamp));
  if (age > 300) {
    return false;
  }
  
  // Compute expected signature
  const signedPayload = `${timestamp}.${payload}`;
  const expected = crypto
    .createHmac('sha256', secret)
    .update(signedPayload)
    .digest('hex');
  
  // Constant-time comparison
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expected)
  );
}
```

---

## 10.7 Client-Side Delivery

For client-side SDK integrations, Scribe Services MAY deliver results via browser messaging mechanisms.

### PostMessage

Scribe SDK sends results to parent EMR application:

```javascript
// Scribe SDK (in iframe) sends:
window.parent.postMessage({
  type: 'medscribealliance:session.completed',
  data: {
    session_id: 'ses_abc123def456',
    status: 'completed',
    templates: { ... },
    transcript: '...'
  }
}, 'https://emr.example.com');
```

EMR application listens:

```javascript
// EMR application receives:
window.addEventListener('message', (event) => {
  // Verify origin
  if (event.origin !== 'https://scribe.example.com') {
    return;
  }
  
  // Handle events
  if (event.data.type === 'medscribealliance:session.completed') {
    const { session_id, templates, transcript } = event.data.data;
    fillEMRForm(templates);
  }
  
  if (event.data.type === 'medscribealliance:session.failed') {
    const { error } = event.data.data;
    showError(error.message);
  }
});
```

### Callback Function

EMR provides callbacks during SDK initialization:

```javascript
// EMR initializes Scribe SDK with callbacks
ScribeSDK.init({
  apiKey: 'sk_live_xxx',  // or use OIDC token
  
  onSessionStarted: (data) => {
    console.log('Session started:', data.session_id);
  },
  
  onSessionCompleted: (data) => {
    const { session_id, templates, transcript } = data;
    fillEMRForm(templates.soap);
    fillMedicationsList(templates.medications);
  },
  
  onSessionFailed: (error) => {
    console.error('Session failed:', error.code, error.message);
    showErrorToUser(error.message);
  },
  
  onSessionExpired: (data) => {
    console.warn('Session expired:', data.session_id);
    promptUserToRestart();
  }
});
```

### PostMessage Event Types

| Event Type | Description |
|------------|-------------|
| `medscribealliance:session.started` | Session created |
| `medscribealliance:session.ended` | Session ended, processing |
| `medscribealliance:session.completed` | Results ready |
| `medscribealliance:session.failed` | Processing failed |
| `medscribealliance:session.expired` | Session timed out |

---

## 10.8 Best Practices

### For EMR Clients

1. **Always verify signatures** before processing webhooks
2. **Respond quickly** (< 30 seconds) to webhook requests
3. **Return 2xx status** on successful receipt
4. **Process asynchronously** - acknowledge receipt, then process
5. **Handle duplicates** - webhooks may be retried
6. **Log webhook events** for debugging

### For Scribe Services

1. **Sign all webhooks** using the registered secret
2. **Include timestamp** in signature for replay protection
3. **Retry on failure** (implementation-specific)
4. **Log delivery attempts** for debugging
5. **Support multiple webhooks** per client if needed

---

**Previous:** [Extraction](./09-extraction.md) | **Next:** [Errors](./11-errors.md)
