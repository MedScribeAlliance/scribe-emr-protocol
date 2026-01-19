# 12. Security Considerations

**MedScribeAlliance Protocol Specification v0.1**

---

## 12.1 Transport Security

### TLS Requirements

- All API endpoints MUST be served over HTTPS
- TLS 1.2 MUST be supported as minimum
- TLS 1.3 SHOULD be supported
- Webhook endpoints MUST be HTTPS

### Certificate Requirements

- Scribe Services MUST use valid certificates from trusted CAs
- Self-signed certificates MUST NOT be used in production
- Certificate expiry SHOULD be monitored

### Recommended Cipher Suites

```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
ECDHE-RSA-AES256-GCM-SHA384
ECDHE-RSA-AES128-GCM-SHA256
```

---

## 12.2 Authentication Security

### API Key Security

| Requirement | Description |
|-------------|-------------|
| Transmission | MUST only be sent in headers, never in URLs |
| Storage | MUST be stored securely (env vars, secrets manager) |
| Exposure | MUST NOT be exposed in client-side code |
| Rotation | SHOULD support rotation without downtime |
| Logging | MUST NOT be logged in plain text |

### OIDC Security

| Requirement | Description |
|-------------|-------------|
| PKCE | MUST use PKCE for all flows |
| State | MUST validate state parameter |
| Nonce | SHOULD use nonce for ID tokens |
| Token Storage | MUST store tokens securely |
| Token Validation | MUST validate all token claims |

### Credential Storage Best Practices

```
✅ Environment variables
✅ Secrets manager (AWS Secrets Manager, HashiCorp Vault)
✅ Encrypted configuration files

❌ Source code
❌ Version control
❌ Client-side JavaScript
❌ URL parameters
❌ Log files
```

---

## 12.3 Audio Data Handling

### In Transit

- Audio MUST be transmitted over HTTPS/TLS
- Audio SHOULD be encrypted if stored temporarily during upload

### At Rest

- Audio SHOULD be encrypted at rest using AES-256 or equivalent
- Encryption keys SHOULD be managed via KMS or similar

### Retention

- Scribe Services SHOULD define clear retention policies
- Audio SHOULD be deleted after processing unless retention is required
- Retention periods SHOULD be communicated to EMR clients

### Access Control

- Audio access SHOULD be limited to processing systems only
- Administrative access to audio SHOULD require additional authorization
- Audit logs SHOULD track all audio access

---

## 12.4 Webhook Security

### Signature Verification

EMR Clients MUST verify webhook signatures:

```python
def verify_webhook(request, secret):
    signature = request.headers.get('X-MSA-Signature')
    if not signature:
        return False
    
    return verify_webhook_signature(
        payload=request.body,
        signature_header=signature,
        secret=secret
    )
```

### Timestamp Validation

- Verify timestamp is within acceptable window (5 minutes recommended)
- Reject old signatures to prevent replay attacks

### IP Allowlisting (Optional)

Scribe Services MAY publish webhook source IPs:

```json
{
  "webhook_source_ips": [
    "203.0.113.0/24",
    "198.51.100.0/24"
  ]
}
```

EMR Clients MAY restrict webhook ingress to these IPs.

---

## 12.5 Data Privacy

### PHI Handling

- **PHI** (Protected Health Information) MUST be handled according to applicable regulations
- Session metadata SHOULD NOT contain PHI
- Transcripts and extractions contain PHI and MUST be protected accordingly

### Data Minimization

- Collect only necessary data
- Don't retain data longer than needed
- Provide mechanisms for data deletion

### Consent

- EMR clients are responsible for obtaining user consent
- Scribe Services SHOULD document data usage in privacy policy

---

## 12.6 Compliance Considerations

### Healthcare Regulations

| Region | Regulation | Key Requirements |
|--------|------------|------------------|
| India | DISHA (proposed) | Data localization, consent |
| India | IT Act 2000 | Data protection, security practices |
| USA | HIPAA | PHI protection, BAA requirements |
| EU | GDPR | Data protection, consent, portability |

### Security Standards

| Standard | Description |
|----------|-------------|
| ISO 27001 | Information security management |
| SOC 2 | Security, availability, confidentiality |
| HIPAA | Healthcare data protection (US) |

### Business Associate Agreement (BAA)

For HIPAA compliance:

- EMR and Scribe SHOULD execute BAA if handling US PHI
- BAA defines responsibilities for PHI protection
- BAA is typically required before integration

---

## 12.7 Rate Limiting

### Purpose

- Prevent abuse and denial of service
- Ensure fair resource allocation
- Protect service stability

### Implementation

Scribe Services SHOULD implement rate limiting:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1705661460

{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Rate limit exceeded"
  }
}
```

### Rate Limit Headers

| Header | Description |
|--------|-------------|
| `X-RateLimit-Limit` | Maximum requests per window |
| `X-RateLimit-Remaining` | Remaining requests in window |
| `X-RateLimit-Reset` | Unix timestamp when limit resets |
| `Retry-After` | Seconds to wait before retrying |

---

## 12.8 Audit Logging

### What to Log

| Event | Data |
|-------|------|
| Authentication | User/client ID, timestamp, success/failure |
| Session creation | Session ID, client ID, timestamp |
| Audio upload | Session ID, chunk info, timestamp |
| Data access | Session ID, accessor, timestamp |
| Webhook delivery | Session ID, URL, status, timestamp |

### Log Security

- Logs MUST NOT contain sensitive data (API keys, audio content)
- Logs SHOULD be stored securely with access controls
- Logs SHOULD be retained per compliance requirements

---

## 12.9 Security Best Practices Summary

### For Scribe Services

| Category | Requirement |
|----------|-------------|
| Transport | HTTPS only, TLS 1.2+ |
| Authentication | Validate all credentials |
| Data | Encrypt at rest and in transit |
| Webhooks | Sign all payloads |
| Logging | Audit all access, don't log secrets |
| Rate limiting | Implement per-client limits |

### For EMR Clients

| Category | Requirement |
|----------|-------------|
| Credentials | Store securely, rotate regularly |
| OIDC | Use PKCE, validate tokens |
| Webhooks | Verify signatures, validate timestamps |
| Data | Handle PHI per regulations |
| Errors | Don't expose internal details to users |

---

## 12.10 Vulnerability Reporting

Scribe Services SHOULD provide a security contact:

```json
{
  "service": {
    "security_contact": "security@example.com",
    "security_policy_url": "https://example.com/.well-known/security.txt"
  }
}
```

Following [security.txt](https://securitytxt.org/) standard is RECOMMENDED.

---

**Previous:** [Errors](./11-errors.md)
