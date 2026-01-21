# MedScribeAlliance Protocol

[![Protocol Version](https://img.shields.io/badge/protocol-v0.1-blue.svg)](./spec/01-introduction.md)
[![Status](https://img.shields.io/badge/status-draft-orange.svg)]()
[![License](https://img.shields.io/badge/license-CC%20BY%204.0-green.svg)](./LICENSE)

**MedScribeAlliance** is an open interoperability protocol that enables Electronic Medical Record (EMR) systems to integrate with any compliant Medical Scribe service for voice-to-structured-medical-text conversion.

## 🎯 Vision

Create a unified standard for medical scribe integrations, allowing:

- **EMR vendors** to integrate once and work with multiple scribe providers
- **Scribe services** to reach more customers without custom integrations per EMR
- **Healthcare providers** to choose the best scribe service for their needs
- **Ecosystem innovation** through standardized interfaces

## 🏗️ Architecture

```
        |─────────────────────────────────────────────────────────────|
        |                                                             ▼
┌─────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│                 │         │                     │         │                 │
│    End User     │────────▶│     EMR Client      │────────▶│  Scribe Service │
│   (Physician/   |         |                     |         |                 |
|    Medical      |         |                     |         |                 |
|   Practitioner) │         │                     │         │                 │
│                 │         │                     │◀────────│                 │
└─────────────────┘         └─────────────────────┘         └─────────────────┘
                                     │
                                     │ Webhook / SDK Callback
                                     ▼
                            ┌─────────────────────┐
                            │   EMR Backend /     │
                            │   Client Browser    │
                            └─────────────────────┘
```

## 📋 Key Features

- **Simple Discovery** - `.well-known/medscribealliance` endpoint for capability discovery
- **Flexible Auth** - API Keys for B2B, OIDC for B2C integrations
- **Streaming Support** - Chunked audio upload for real-time capture
- **Template-based Extraction** - SOAP notes, medications, discharge summaries, and custom templates
- **Async Results** - Webhook delivery with signature verification
- **Multi-language** - Built for India's diverse language landscape

## 📖 Specification

| Document | Description |
|----------|-------------|
| [Introduction](./spec/01-introduction.md) | Purpose, scope, and conformance requirements |
| [Architecture](./spec/02-architecture.md) | Integration patterns and high-level flow |
| [Versioning](./spec/03-versioning.md) | Protocol version negotiation |
| [Discovery](./spec/04-discovery.md) | Well-known endpoint and capability schema |
| [Authentication](./spec/05-authentication.md) | API Key and OIDC authentication |
| [Sessions](./spec/06-sessions.md) | Session lifecycle management |
| [Audio Ingestion](./spec/07-audio-ingestion.md) | Audio upload methods and formats |
| [Templates](./spec/08-templates.md) | Template listing and standard templates |
| [Extraction](./spec/09-extraction.md) | Response structure and output formats |
| [Webhooks](./spec/10-webhooks.md) | Event delivery and signature verification |
| [Errors](./spec/11-errors.md) | Error codes and handling |
| [Security](./spec/12-security.md) | Security considerations |

## 🚀 Quick Start

### For EMR Implementers

1. **Discover capabilities**
   ```bash
   curl https://scribe.example.com/.well-known/medscribealliance
   ```

2. **Create a session**
   ```bash
   curl -X POST https://api.scribe.example.com/v1/sessions \
     -H "X-API-Key: sk_live_xxx" \
     -H "Content-Type: application/json" \
     -d '{"templates": ["soap", "medications"]}'
   ```

3. **Upload audio**
   ```bash
   curl -X POST https://api.scribe.example.com/v1/sessions/{id}/audio \
     -H "X-API-Key: sk_live_xxx" \
     -H "Content-Type: audio/webm;codecs=opus" \
     --data-binary @recording.webm
   ```

4. **End session & receive results via webhook**
   ```bash
   curl -X POST https://api.scribe.example.com/v1/sessions/{id}/end \
     -H "X-API-Key: sk_live_xxx"
   ```

### For Scribe Service Implementers

1. Implement the [Discovery](./spec/04-discovery.md) endpoint
2. Support at least one [Authentication](./spec/05-authentication.md) method
3. Implement [Session](./spec/06-sessions.md) and [Audio](./spec/07-audio-ingestion.md) endpoints
4. Return structured data per [Extraction](./spec/09-extraction.md) spec
5. Deliver results via [Webhooks](./spec/10-webhooks.md)

## 📁 Repository Structure

```
medscribealliance/
├── README.md                 # This file
├── LICENSE                   # CC BY 4.0
├── CONTRIBUTING.md           # Contribution guidelines
├── CHANGELOG.md              # Version history
├── spec/                     # Protocol specification
│   ├── 01-introduction.md
│   ├── 02-architecture.md
│   ├── 03-versioning.md
│   ├── 04-discovery.md
│   ├── 05-authentication.md
│   ├── 06-sessions.md
│   ├── 07-audio-ingestion.md
│   ├── 08-templates.md
│   ├── 09-extraction.md
│   ├── 10-webhooks.md
│   ├── 11-errors.md
│   └── 12-security.md
├── examples/                 # Example payloads and flows
│   ├── discovery-document.json
│   ├── session-flow.md
│   └── webhook-payloads.json
└── schemas/                  # JSON schemas (future)
    └── README.md
```

## 🤝 Contributing

We welcome contributions from:

- EMR vendors
- Scribe service providers
- Healthcare IT professionals
- Standards organizations

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

### How to Contribute

1. **Open an Issue** - For bugs, questions, or feature requests
2. **Submit a PR** - For spec clarifications or additions
3. **Join Discussions** - Participate in GitHub Discussions
4. **Implement & Feedback** - Build implementations and share learnings

## 📋 Roadmap

### v0.1 (Current - Draft)
- [x] Core session lifecycle
- [x] Audio ingestion (chunked & single)
- [x] Template-based extraction
- [x] Webhook delivery
- [x] API Key & OIDC authentication

### v0.2 (Planned)
- [ ] Real-time transcription streaming
- [ ] FHIR bundle output mapping
- [ ] Template creation API
- [ ] Conformance test suite

### v1.0 (Future)
- [ ] Stable API freeze
- [ ] Reference implementations
- [ ] Certification program

## 📜 License

This specification is released under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to:
- **Share** — copy and redistribute the material
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit

## 📞 Contact

- **Working Group:** MedScribeAlliance Working Group
- **Email:** [TBD]
- **Discussions:** [GitHub Discussions](../../discussions)

---

<p align="center">
  <i>Building the future of medical documentation interoperability</i>
</p>
