# 1. Introduction

**MedScribeAlliance Protocol Specification v0.1**

---

## 1.1 Purpose

The MedScribeAlliance Protocol defines a standard interface for interoperability between Electronic Medical Record (EMR) systems and Medical Scribe services. This protocol enables EMR clients to integrate with any compliant scribe service for voice-to-structured-medical-text conversion, promoting vendor choice and ecosystem innovation.

## 1.2 Scope

### In Scope

This specification covers:

- Discovery of scribe service capabilities
- Authentication mechanisms for both B2B and B2C integrations
- Voice data upload (single and chunked)
- Template-based structured data extraction
- Asynchronous result delivery via webhooks
- Client-side SDK integration patterns

### Out of Scope

This specification does NOT cover:

- FHIR bundle structure (separate specification)
- Internal scribe processing implementation
- Billing and payment reconciliation details
- Custom template creation interfaces
- Speaker diarization specifics (vendor capability)
- Resume/retry mechanisms (vendor capability)

## 1.3 Terminology

| Term | Definition |
|------|------------|
| **EMR Client** | Electronic Medical Record system integrating with a scribe service |
| **Scribe Service** | Voice-to-text transcription and medical information extraction service |
| **Session** | A single voice capture and extraction workflow |
| **Template** | A structured output format for extracted medical information |
| **Transcript** | Raw voice-to-text conversion output |
| **B2B Integration** | Direct EMR-to-Scribe integration where EMR is the customer |
| **B2C Integration** | User-authorized integration where users have direct relationship with Scribe |

## 1.4 Conformance Requirements

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

### Scribe Service Conformance

A conformant **Scribe Service** implementation:

- MUST implement all endpoints marked as REQUIRED
- MUST publish a valid discovery document at `/.well-known/medscribealliance`
- MUST support at least one authentication mechanism (API Key or OIDC)
- MUST support at least one audio upload method (chunked OR single)
- MUST generate complete transcript for every session
- MUST explicitly define session expiry behavior
- SHOULD support webhook delivery of results
- SHOULD support multiple audio formats

### EMR Client Conformance

A conformant **EMR Client** implementation:

- MUST discover scribe capabilities before initiating sessions
- MUST use supported audio formats as declared in discovery
- MUST explicitly end sessions using the end session endpoint
- MUST verify webhook signatures before processing
- SHOULD implement webhook receivers for asynchronous results
- SHOULD handle template unavailability gracefully

## 1.5 Notational Conventions

### HTTP Examples

HTTP request and response examples use the following format:

```http
POST /sessions HTTP/1.1
Host: api.scribe.example.com
Authorization: X-API-Key sk_live_xxx
Content-Type: application/json

{
  "templates": ["soap"]
}
```

### JSON Examples

JSON examples are formatted for readability. Actual implementations may use compact JSON.

### Placeholders

- `{session_id}` - Variable path parameter
- `sk_live_xxx` - Example API key (not real)
- `example.com` - Example domain

---

**Next:** [Architecture](./02-architecture.md)
