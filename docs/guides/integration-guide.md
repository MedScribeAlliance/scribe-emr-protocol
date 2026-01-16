# Integration Guide

This guide provides deep technical details for implementing SEP. It is intended for EMR engineers building the client-side integration.

## 1. Wire Traces: The Lifecycle

### Step 0: Initialization Handshake

**Request**
```http
POST /initialize HTTP/1.1
Host: api.scribeprovider.com
Content-Type: application/json

{
  "protocolVersion": "2024-01-01",
  "clientInfo": { "name": "HospitalEMR", "version": "1.0.0" }
}
```

**Response**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "protocolVersion": "2024-01-01",
  "serverInfo": { "name": "ScribePro", "version": "2.5" },
  "templates": [ { "id": "soap_v1" } ]
}
```

### Step A: Submitting the Audio

**Request**
```http
POST /process/async HTTP/1.1
Host: api.scribeprovider.com
Authorization: Bearer sk_live_12345
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="request"

{
  "template_id": "soap_v1",
  "config": {
    "webhook_url": "https://emr.hospital.org/webhooks/incoming"
  },
  "context": {
    "patient": { "id": "p_555" }
  }
}
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="patient_visit.mp3"
Content-Type: audio/mpeg

<BINARY_AUDIO_DATA>
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

**Response**
```http
HTTP/1.1 202 Accepted
Content-Type: application/json

{
  "job_id": "job_8899aabb",
  "status": "queued",
  "eta_seconds": 45
}
```

### Step B: Receiving the Webhook

When processing is complete, the Scribe server calls your webhook.

**Request (Scribe -> EMR)**
```http
POST /webhooks/incoming HTTP/1.1
Host: emr.hospital.org
Content-Type: application/json
X-Scribe-Signature: sha256=a1b2c3d4...

{
  "job_id": "job_8899aabb",
  "status": "completed",
  "completed_at": "2023-11-01T10:05:00Z",
  "output": {
    "transcription": "Patient reports...",
    "structured_data": {
      "soap": { "subjective": "..." }
    }
  }
}
```

**Response (EMR -> Scribe)**
```http
HTTP/1.1 200 OK
```

---

## 2. Resiliency & Reliability

### Handling Rate Limits (429)
Scribe providers may enforce rate limits. If you receive a `429 Too Many Requests`, you MUST respect the `Retry-After` header.

**Recommendation**: Implement **Exponential Backoff**.
1.  Wait 1s.
2.  Retry.
3.  If fail, wait 2s.
4.  Retry.
5.  If fail, wait 4s...

### Webhook Failures
If your server returns a `5xx` error or times out during the Webhook call, the Scribe provider generally retries with exponential backoff (e.g., at 1m, 5m, 15m, 1h).

**Best Practice**: Ensure your webhook handler is **idempotent**. Processing the same `job_id` twice should not result in duplicate notes in the user's chart.

## 3. Timeout Configuration

Recommended client-side timeouts:

| Operation | Recommended Timeout | Reason |
| :--- | :--- | :--- |
| `GET /capabilities` | 5s | API is lightweight; fail fast if down. |
| `POST /process` (Sync) | 60s | Processing takes time (approx 1x audio duration). |
| `POST /process/async` | 30s | Just an upload; longer for large files. |
| `GET /jobs/{id}` | 5s | Simple status check. |
