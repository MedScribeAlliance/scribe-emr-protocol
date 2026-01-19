# 2. Architecture Overview

**MedScribeAlliance Protocol Specification v0.1**

---

## 2.1 Actors

The protocol involves three primary actors:

```
┌─────────────────┐         ┌─────────────────────┐         ┌─────────────────┐
│                 │         │                     │         │                 │
│    End User     │────────▶│     EMR Client      │────────▶│  Scribe Service │
│   (Physician)   │         │                     │         │                 │
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

| Actor | Description |
|-------|-------------|
| **End User** | Physician or healthcare provider using voice to document patient encounters |
| **EMR Client** | Electronic Medical Record system that captures voice and displays structured results |
| **Scribe Service** | Backend service that processes audio and extracts structured medical information |

## 2.2 Integration Patterns

The protocol supports three primary integration patterns:

### 2.2.1 Direct EMR Integration (B2B)

EMR integrates directly with Scribe Service using API keys. The EMR is the customer of the Scribe Service and manages billing internally with their users.

```
┌─────────────────┐                    ┌─────────────────┐
│                 │                    │                 │
│   EMR Backend   │─── API Key ───────▶│  Scribe Service │
│                 │                    │                 │
│                 │◀── Webhook ────────│                 │
└─────────────────┘                    └─────────────────┘
```

**Characteristics:**
- EMR authenticates with API key
- Scribe bills EMR (not end users)
- EMR manages user access internally
- Simpler integration for enterprise deployments

**Use Cases:**
- EMR vendors bundling scribe functionality
- Enterprise healthcare systems
- White-label scribe integrations

### 2.2.2 User-Authorized Integration (B2C)

End users authenticate directly with the Scribe Service via OIDC. Users have a direct relationship and billing with the Scribe Service.

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │         │                 │
│    End User     │───┐     │   EMR Client    │         │  Scribe Service │
│                 │   │     │                 │         │                 │
└─────────────────┘   │     └────────┬────────┘         └────────┬────────┘
                      │              │                           │
                      │   ┌──────────▼───────────────────────────▼──┐
                      │   │                                         │
                      └──▶│   OIDC Authorization (redirect/popup)   │
                          │                                         │
                          └─────────────────────────────────────────┘
```

**Characteristics:**
- User authenticates directly with Scribe
- User has direct billing relationship
- EMR acts as OIDC client (relying party)
- User controls their scribe subscription

**Use Cases:**
- Marketplace model
- Individual physician subscriptions
- Multi-scribe vendor environments

### 2.2.3 Client-Side SDK Pattern

EMR embeds a Scribe SDK in their frontend. Audio capture and upload happens client-side, with results delivered via browser messaging or callbacks.

```
┌───────────────────────────────────────────────────────┐
│                    EMR Frontend                       │
│                                                       │
│   ┌───────────────────────────────────────────────┐   │
│   │           Scribe SDK (iframe/JS)              │   │
│   │                                               │   │
│   │   ┌─────────┐    ┌────────┐    ┌─────────┐   │   │
│   │   │  Audio  │───▶│ Upload │───▶│ Process │   │   │
│   │   │ Capture │    │        │    │         │   │   │
│   │   └─────────┘    └────────┘    └────┬────┘   │   │
│   │                                     │        │   │
│   └─────────────────────────────────────┼────────┘   │
│                                         │            │
│              postMessage / callback     │            │
│                                         ▼            │
│   ┌───────────────────────────────────────────────┐  │
│   │           EMR Form Fill Logic                 │  │
│   └───────────────────────────────────────────────┘  │
│                                                       │
└───────────────────────────────────────────────────────┘
```

**Characteristics:**
- Audio captured in browser
- Direct upload to Scribe from client
- Results delivered via postMessage or callback
- Minimal EMR backend involvement

**Use Cases:**
- Rich browser-based EMR applications
- Rapid integration with minimal backend changes
- Real-time transcription display

## 2.3 High-Level Protocol Flow

```
┌──────────┐                    ┌──────────────┐                    ┌──────────────┐
│   EMR    │                    │    Scribe    │                    │   Webhook    │
│  Client  │                    │   Service    │                    │   Receiver   │
└────┬─────┘                    └──────┬───────┘                    └──────┬───────┘
     │                                 │                                   │
     │  1. GET /.well-known/           │                                   │
     │     medscribealliance           │                                   │
     │────────────────────────────────▶│                                   │
     │◀────────────────────────────────│                                   │
     │         Discovery Document      │                                   │
     │                                 │                                   │
     │  2. POST /sessions              │                                   │
     │     {templates, metadata}       │                                   │
     │────────────────────────────────▶│                                   │
     │◀────────────────────────────────│                                   │
     │         {session_id}            │                                   │
     │                                 │──────────────────────────────────▶│
     │                                 │   Webhook: session.started        │
     │                                 │                                   │
     │  3. POST /sessions/{id}/audio   │                                   │
     │     [audio chunks]              │                                   │
     │────────────────────────────────▶│                                   │
     │◀────────────────────────────────│                                   │
     │         {chunk_received}        │                                   │
     │                                 │                                   │
     │  4. POST /sessions/{id}/end     │                                   │
     │────────────────────────────────▶│                                   │
     │◀────────────────────────────────│                                   │
     │         {processing}            │                                   │
     │                                 │──────────────────────────────────▶│
     │                                 │   Webhook: session.ended          │
     │                                 │                                   │
     │                                 │         [Processing...]           │
     │                                 │                                   │
     │                                 │──────────────────────────────────▶│
     │                                 │   Webhook: session.completed      │
     │                                 │   {templates, transcript}         │
     │                                 │                                   │
     │  5. GET /sessions/{id}          │                                   │
     │     (optional polling)          │                                   │
     │────────────────────────────────▶│                                   │
     │◀────────────────────────────────│                                   │
     │         {extraction data}       │                                   │
     │                                 │                                   │
```

### Flow Steps

| Step | Description |
|------|-------------|
| **1. Discovery** | EMR fetches scribe capabilities, supported formats, models |
| **2. Session Creation** | EMR creates session with desired templates and metadata |
| **3. Audio Upload** | EMR uploads audio (chunked or single file) |
| **4. End Session** | EMR explicitly ends session, triggering processing |
| **5. Result Retrieval** | Results delivered via webhook or polling |

## 2.4 Data Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│    Voice    │────▶│   Audio     │────▶│  Transcript │────▶│  Structured │
│    Input    │     │   Upload    │     │  Generation │     │    Data     │
│             │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                    ┌──────────────────────────────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │               │
            │   Templates   │
            │   - SOAP      │
            │   - Meds      │
            │   - Custom    │
            │               │
            └───────────────┘
```

---

**Previous:** [Introduction](./01-introduction.md) | **Next:** [Versioning](./03-versioning.md)
