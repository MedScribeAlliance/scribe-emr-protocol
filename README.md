# Medical Scribe Alliance: Scribe EMR Protocol (SEP)
## Scribe EMR Protocol

**SEP** is a standard protocol designed to enable seamless interoperability between Electronic Medical Record (EMR) systems and AI Scribe solutions.

Typically, every EMR integration with a Scribe vendor requires a custom API implementation. SEP unifies this by defining a foundational protocol—similar to how [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) standardizes AI tool context.

## 📚 Documentation

1.  **[Architecture Overview](docs/architecture.md)**: Conceptual model, roles, and high-level workflows.
2.  **[Protocol Specification](docs/protocol-spec.md)**: The normative HTTP API specification (Endpoints, Headers, Webhooks).
3.  **[Data Models](docs/data-models.md)**: JSON Schemas for requests, responses, and template definitions.

### 📘 Advanced Guides
*   **[Integration Guide](docs/guides/integration-guide.md)**: Wire traces, resilience patterns, and timeouts.
*   **[Security & Compliance](docs/security.md)**: HIPAA, mTLS, and Data Retention.
*   **[Error Catalog](docs/errors.md)**: Comprehensive list of error codes and recovery actions.


## 🚀 Key Features

*   **Standardized Discovery**: EMRs can dynamically query what "Templates" (note types) a Scribe supports.
*   **Authentication Agnostic**: Works with standard OAuth2 / Bearer token flows.
*   **Flexible Modalities**:
    *   **Sync**: For short, immediate commands.
    *   **Async**: For standard consultations (Webhook callback).
    *   **Chunked**: For real-time streaming or poor network conditions.
*   **Structured Output**: Defines how to return clinical notes, FHIR bundles, and raw transcripts.

## 🛠 Getting Started for Implementers

### For EMR Developers
1.  Implement the **Discovery** flow (`GET /capabilities`) to show available tools in your UI.
2.  Implement the **Authentication** handshake provided by your Scribe partner.
3.  Choose your **Audio Submission** strategy (Async is recommended for robustness).
4.  Set up a **Webhook Listener** to receive completed notes.

### For Scribe Vendors
1.  Expose the SEP-compliant endpoints.
2.  Map your internal note types to the SEP `Template` structure.
3.  Ensure your system can handle the standard JSON payloads for context and output.

---
*Maintained by the Medical Scribe Alliance.*
