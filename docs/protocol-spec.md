# SEP Protocol Specification v1.0

## 1. Introduction
This specification defines the HTTP/REST API for the Scribe EMR Protocol. 

**Base URL**: `https://api.scribeprovider.com/v1/sep` (Example)

## 2. Authentication
All requests MUST include the `Authorization` header.
`Authorization: Bearer <access_token>`

## 3. Initialization Handshake

Before any transcription can occur, the Client (EMR) and Server (Scribe) must negotiate capabilities and agree on the protocol version.

### Initialize
The Client initiates the handshake.

**Request**
`POST /initialize`

```json
{
  "protocolVersion": "2024-01-01",
  "clientInfo": {
    "name": "MyEMR",
    "version": "4.5.0"
  },
  "capabilities": {
    "sampling": {}
  }
}
```

**Response (200 OK)**
```json
{
  "protocolVersion": "2024-01-01",
  "serverInfo": {
    "name": "SuperScribe AI",
    "version": "1.2.0"
  },
  "capabilities": {
    "logging": {},
    "prompts": {} // In SEP context, this lists supported functionality
  },
  "templates": [
    { "id": "soap_general", "name": "General SOAP" },
    { "id": "referral_letter", "name": "Referral Letter" }
  ]
}
```


## 4. Structuring API

### A. Synchronous Structuring
Upload audio and context, wait for the result.
*Note: Only suitable for short audio (< 60s).*

**Request**
`POST /process`
**Content-Type**: `multipart/form-data`

*   `request`: (JSON String) `StructRequest` object.
    ```json
    {
      "templates": ["soap_v1", "verbatim_transcript"],
      "context": { ... },
      "config": { "webhook_url": "..." }
    }
    ```
*   `file`: (Binary) Audio file.

**Response**
*   **200 OK**: Returns `StructResponse`.
    ```json
    {
      "job_id": "...",
      "status": "completed",
      "results": {
        "soap_v1": { "subjective": "..." },
        "verbatim_transcript": "Patient said..."
      }
    }
    ```

### B. Asynchronous Structuring
Submit job, receive ID, wait for Webhook.

**Request**
`POST /process/async`
**Content-Type**: `multipart/form-data`

*   `request`: (JSON String) `ScribeRequest` object (MUST include `config.webhook_url`).
*   `file`: (Binary) Audio file.

**Response**
*   **202 Accepted**
```json
{
  "job_id": "job_12345",
  "status": "queued",
  "eta_seconds": 120
}
```

### C. Chunked Upload (Session-Based)
For streaming or uploading large files in parts.

#### Step 1: Create Session
**Request**
`POST /session`
**Body**: `ScribeRequest` (excluding audio config)

**Response (201 Created)**
```json
{ "session_id": "sess_abc" }
```

#### Step 2: Upload Audio Chunk
**Request**
`POST /session/{session_id}/audio`
**Headers**:
*   `X-Audio-Sequence`: Integer (0, 1, 2...)
*   `Content-Type`: `audio/wav` (or specific binary type)

**Body**: Raw binary audio chunk.

**Response (200 OK)**

#### Step 3: Commit / Finalize
Trigger processing after all chunks are sent.

**Request**
`POST /session/{session_id}/commit`

**Response (202 Accepted)**
```json
{ "job_id": "job_from_sess_abc" }
```

## 5. Result Retrieval

### Get Job Status / Result
Poll for status or retrieve result manually if webhook fails.

**Request**
`GET /jobs/{job_id}`

**Response**
*   **200 OK**: `JobResult` (Status: "processing" or "completed").

## 6. Webhooks

When an async job completes, the Scribe server sends a POST request to the `webhook_url` provided in the request.

**Request (from Scribe to EMR)**
`POST <webhook_url>`
**Body**: `JobResult`
