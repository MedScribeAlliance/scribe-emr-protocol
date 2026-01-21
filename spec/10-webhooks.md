# 10. Webhooks

**MedScribeAlliance Protocol Specification v0.1**

---

## 10.1 Overview

Webhooks provide real-time event notifications to EMR clients when session state changes occur. This protocol uses an **event notification model** where webhooks contain only event metadata, and full session data is retrieved via the authenticated `GET /sessions/{id}` API.

```
┌─────────────────┐                    ┌─────────────────┐
│                 │   Event Notification│                 │
│  Scribe Service │──────────────────▶│   EMR Backend   │
│                 │   (session_id only) │                 │
└─────────────────┘                    └────────┬────────┘
                                                │
       ┌────────────────────────────────────────┘
       │  GET /sessions/{id}
       │  (with authentication)
       ▼
┌─────────────────┐
│  Full Session   │
│  Data Response  │
└─────────────────┘
```

### Benefits of Event Notification Model

| Benefit | Description |
|---------|-------------|
| **Lightweight payloads** | Only event type and session_id transmitted |
| **Security simplified** | No sensitive data in webhook; signature verification optional |
| **Consistent data access** | All data retrieval through authenticated API |
| **Reduced complexity** | EMR handles one data format from status API |
| **Standard pattern** | Common approach used by Stripe, GitHub, and other APIs |

---

## 10.2 Webhook Registration

**Endpoint:** Discovered via `endpoints.webhooks_url` in the [discovery document](./04-discovery.md)

**Required:** RECOMMENDED

Registers a webhook endpoint to receive session event notifications.

### Discovering the Webhook Endpoint

The webhook registration URL is provided in the well-known discovery document:

```json
{
  "endpoints": {
    "base_url": "https://api.scribe.example.com/v1",
    "webhooks_url": "https://api.scribe.example.com/v1/webhooks"
  }
}
```

EMR clients MUST use the `webhooks_url` from the discovery document rather than constructing the URL manually.

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
    "session.partial",
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
| `secret` | string | No | Secret for optional signature verification |

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
    "session.partial",
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
| `session.completed` | Extraction complete, all results available | After successful processing |
| `session.partial` | Extraction complete, partial results available | After processing with some failures |
| `session.failed` | Processing failed entirely | After processing failure |
| `session.expired` | Session timed out | After session timeout |

---

## 10.5 Webhook Payload Structure

All webhook payloads are lightweight event notifications containing only the event type and session identifier. No sensitive data (transcripts, templates, patient information) is included.

### Payload Format

```json
{
  "event": "session.completed",
  "timestamp": "2025-01-19T10:35:00Z",
  "session_id": "ses_abc123def456"
}
```

### Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `event` | string | Event type (e.g., `session.completed`) |
| `timestamp` | string | ISO 8601 timestamp of the event |
| `session_id` | string | Session identifier for data retrieval |

### Event Payloads

All events use the same simple structure:

**session.started**
```json
{
  "event": "session.started",
  "timestamp": "2025-01-19T10:30:00Z",
  "session_id": "ses_abc123def456"
}
```

**session.ended**
```json
{
  "event": "session.ended",
  "timestamp": "2025-01-19T10:32:00Z",
  "session_id": "ses_abc123def456"
}
```

**session.completed**
```json
{
  "event": "session.completed",
  "timestamp": "2025-01-19T10:35:00Z",
  "session_id": "ses_abc123def456"
}
```

**session.partial**
```json
{
  "event": "session.partial",
  "timestamp": "2025-01-19T10:35:00Z",
  "session_id": "ses_abc123def456"
}
```

**session.failed**
```json
{
  "event": "session.failed",
  "timestamp": "2025-01-19T10:35:00Z",
  "session_id": "ses_abc123def456"
}
```

**session.expired**
```json
{
  "event": "session.expired",
  "timestamp": "2025-01-19T11:30:00Z",
  "session_id": "ses_abc123def456"
}
```

---

## 10.6 Retrieving Session Data

After receiving a webhook notification, EMR clients retrieve full session data via the authenticated status API.

### Flow

```
1. Receive webhook → { event: "session.completed", session_id: "ses_abc123" }
2. Extract session_id
3. Call GET /sessions/ses_abc123 with authentication
4. Process full session data (templates, transcript, etc.)
```

### Example

```http
GET /sessions/ses_abc123def456 HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
```

```json
{
  "session_id": "ses_abc123def456",
  "status": "completed",
  "created_at": "2025-01-19T10:30:00Z",
  "completed_at": "2025-01-19T10:35:00Z",
  "model_used": "pro",
  "language_detected": "en",
  "audio_files_received": 3,
  "audio_files": ["audio_0.webm", "audio_1.webm", "audio_2.webm"],
  "additional_data": {
    "emr_encounter_id": "enc_123"
  },
  "templates": {
    "soap": {
      "status": "success",
      "data": { ... }
    }
  },
  "transcript": "Doctor: Good morning..."
}
```

See [Sessions](./06-sessions.md) and [Extraction](./09-extraction.md) for full response structure.

---

## 10.7 Signature Verification (Optional)

Since webhooks contain no sensitive data, signature verification is **optional but recommended** for verifying webhook authenticity.

### When to Use Signature Verification

| Scenario | Recommendation |
|----------|----------------|
| High-security environments | Recommended |
| Public-facing webhook endpoints | Recommended |
| Internal/VPN-protected endpoints | Optional |
| Development/testing | Optional |

### Signature Header

If a secret was provided during registration, webhooks include a signature:

```http
POST /scribe-webhook HTTP/1.1
Host: emr.example.com
Content-Type: application/json
X-MSA-Signature: t=1705661400,v1=5257a869e7ecebeda32affa62cdca3fa51cded5fa20f8de7...

{"event":"session.completed","timestamp":"2025-01-19T10:35:00Z","session_id":"ses_abc123def456"}
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

```
signed_payload = "{timestamp}.{raw_request_body}"
signature = HMAC-SHA256(secret, signed_payload)
```

### Verification Example (Python)

```python
import hmac
import hashlib

def verify_webhook_signature(payload: bytes, signature_header: str, secret: str) -> bool:
    parts = dict(item.split('=', 1) for item in signature_header.split(','))
    timestamp = parts.get('t')
    signature = parts.get('v1')

    if not timestamp or not signature:
        return False

    signed_payload = f"{timestamp}.{payload.decode('utf-8')}"
    expected = hmac.new(
        secret.encode('utf-8'),
        signed_payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
```

---

## 10.8 Client-Side Delivery

For client-side SDK integrations, Scribe Services MAY deliver event notifications via browser messaging mechanisms.

### PostMessage

```javascript
// Scribe SDK (in iframe) sends event notification:
window.parent.postMessage({
  type: 'medscribealliance:session.completed',
  session_id: 'ses_abc123def456'
}, 'https://emr.example.com');
```

```javascript
// EMR application receives and fetches data:
window.addEventListener('message', async (event) => {
  if (event.origin !== 'https://scribe.example.com') {
    return;
  }

  if (event.data.type === 'medscribealliance:session.completed') {
    // Fetch full data via API
    const response = await fetch(`/api/sessions/${event.data.session_id}`);
    const sessionData = await response.json();
    fillEMRForm(sessionData.templates);
  }
});
```

### PostMessage Event Types

| Event Type | Description |
|------------|-------------|
| `medscribealliance:session.started` | Session created |
| `medscribealliance:session.ended` | Session ended, processing |
| `medscribealliance:session.completed` | Processing complete |
| `medscribealliance:session.partial` | Partial results ready |
| `medscribealliance:session.failed` | Processing failed |
| `medscribealliance:session.expired` | Session timed out |

---

## 10.9 Best Practices

### For EMR Clients

1. **Respond quickly** (< 30 seconds) to webhook requests
2. **Return 2xx status** immediately on receipt
3. **Fetch data asynchronously** after acknowledging webhook
4. **Handle duplicates** - webhooks may be retried; use session_id for deduplication
5. **Implement retry logic** for status API calls
6. **Log webhook events** for debugging

### For Scribe Services

1. **Keep payloads minimal** - only event type and session_id
2. **Retry on failure** with exponential backoff
3. **Log delivery attempts** for debugging
4. **Include signature** if secret was provided during registration
5. **Support multiple webhooks** per client if needed

---

**Previous:** [Extraction](./09-extraction.md) | **Next:** [Errors](./11-errors.md)
