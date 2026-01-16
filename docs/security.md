# Security & Compliance

Given the sensitivity of Protected Health Information (PHI), SEP implementations must adhere to strict security standards.

## 1. Transport Security

*   **HTTPS Required**: All traffic MUST use TLS 1.2 or higher. Unencrypted HTTP is strictly prohibited.
*   **Cipher Suites**: Servers should enforce Forward Secrecy (FS).

## 2. Authentication

### Client Authentication
Scribe providers typically issue two types of credentials:
1.  **API Keys**: `Authorization: Bearer <key>`. Simple, long-lived. rotate frequently.
2.  **OAuth2 (Client Credentials)**: Recommended for enterprise integrations. The EMR requests a short-lived Access Token.

### Webhook Verification
To ensure a webhook request is genuinely from the Scribe provider:
1.  **Shared Secret**: Used to compute an HMAC-SHA256 signature.
2.  **Validation**: The EMR calculates the hash of the payload and compares it to the `X-Scribe-Signature` header.

## 3. Data Privacy & HIPAA

### Data Minimization
While the `ContextPayload` allows sending patient demographics, **send only what is necessary**.
*   **Preferred**: Send internal IDs (`"id": "pat_555"`) rather than names if the Scribe does not need the name for the note.
*   **Dates**: Use ISO 8601 (`YYYY-MM-DD`).

### Data Retention
Scribe providers generally operate in two modes:
1.  **Zero Retention**: Audio and transcripts are deleted immediately after delivery. (Preferred for maximum privacy).
2.  **Training Allowed**: Data is de-identified and used to improve models. **This requires explicit consent and BAA provisions.**

### Business Associate Agreement (BAA)
Under HIPAA, the Scribe provider acts as a Business Associate to the Covered Entity (EMR/Hospital). A BAA must be in place before any PHI is transmitted via SEP.
