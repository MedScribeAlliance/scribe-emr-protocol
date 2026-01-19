# Changelog

All notable changes to the MedScribeAlliance Protocol specification will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Real-time transcription streaming specification
- FHIR bundle output mapping
- Template creation API
- Conformance test suite

---

## [0.1.0] - 2025-01-19

### Added

#### Core Protocol
- Discovery mechanism via `/.well-known/medscribealliance`
- Protocol versioning with `MSA-Version` header
- Backward compatibility guidelines

#### Authentication
- API Key authentication for B2B integrations
- OIDC authentication with PKCE for B2C integrations
- Hybrid authentication model supporting both patterns

#### Session Management
- Session creation with template selection
- Session lifecycle states (created, recording, processing, completed, failed, expired)
- Explicit session end requirement
- Metadata pass-through for EMR correlation

#### Audio Ingestion
- Chunked audio upload (≤20 seconds per chunk)
- Single file upload
- Multiple audio format support (WebM Opus, WAV, OGG)

#### Templates
- Standard template definitions (SOAP, medications, transcript, etc.)
- Template listing endpoint
- Partial success handling for multiple templates
- Custom template support (interface out of scope)

#### Extraction
- Structured response format
- Template-specific output schemas
- Transcript inclusion option
- Template error reporting

#### Webhooks
- Webhook registration and management
- Five event types: session.started, session.ended, session.completed, session.failed, session.expired
- HMAC-SHA256 signature verification
- Client-provided webhook secrets
- Client-side delivery via PostMessage/callbacks

#### Security
- TLS requirements
- Authentication security guidelines
- Webhook signature verification
- Data handling recommendations
- Compliance considerations (HIPAA, DISHA, GDPR)

#### Error Handling
- Standard error response format
- Comprehensive error code definitions
- HTTP status code mapping
- Retry guidelines

### Notes
- Initial draft specification
- Focused on India's multi-language healthcare ecosystem
- Designed for both B2B and B2C integration patterns

---

## Version History Summary

| Version | Date | Status | Key Changes |
|---------|------|--------|-------------|
| 0.1.0 | 2025-01-19 | Draft | Initial specification |

---

[Unreleased]: https://github.com/medscribealliance/spec/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/medscribealliance/spec/releases/tag/v0.1.0
