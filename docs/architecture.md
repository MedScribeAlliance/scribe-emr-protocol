# SEP Architecture & Concepts

The **Scribe EMR Protocol (SEP)** defines a standard protocol for interoperability between Electronic Medical Record (EMR) systems and AI Scribe solutions.

## Core Concepts

### Roles
*   **EMR (Client)**: The system of record (Electronic Medical Record) that holds patient data and initiates requests for transcription.
*   **Scribe (Server)**: The AI-powered service that accepts audio/context and returns structured medical documentation (notes, FHIR resources, etc.).

### Resources
*   **Template**: A definition of the output format offered by the Scribe (e.g., "SOAP Note", "Cardiology Consult", "Psychiatric Evaluation").
*   **Session**: A stateful interaction context representing a single medical encounter being recorded.
*   **Job**: An asynchronous task handling the transcription/generation process.

## High-Level Workflows

### 1. Initialization Handshake
The interaction begins with a bidirectional handshake to exchange capabilities and versions.

```mermaid
sequenceDiagram
    participant EMR
    participant Scribe
    
    EMR->>Scribe: POST /initialize (Client Info)
    Scribe-->>EMR: 200 OK (Server Info + Templates)
    
    Note right of EMR: Connection Established
```


### 2. Transcription Modalities

SEP supports three modalities to accommodate different network conditions and user workflows.

#### A. Synchronous (Short Audio)
Best for short dictations or commands where immediate feedback is required. The EMR holds the connection open until processing is complete.

```mermaid
sequenceDiagram
    participant EMR
    participant Scribe
    
    EMR->>Scribe: POST /process (Audio + Context)
    Note over Scribe: Processing...
    Scribe-->>EMR: 200 OK (Structured Output)
```

#### B. Asynchronous (Long Audio / Background)
Best for full consultations. The EMR submits the job and receives a Job ID. The Scribe calls a webhook when done.

```mermaid
sequenceDiagram
    participant EMR
    participant Scribe
    
    EMR->>Scribe: POST /process/async (Audio + Context + WebhookURL)
    Scribe-->>EMR: 202 Accepted (Job ID)
    
    Note over Scribe: Processing...
    
    Scribe->>EMR: POST <WebhookURL> (Result Payload)
    EMR-->>Scribe: 200 OK
```

#### C. Chunked / Streaming (Real-time or Unstable Network)
Allows uploading audio in parts. Essential for long recordings or when recording is happening live.

```mermaid
sequenceDiagram
    participant EMR
    participant Scribe
    
    EMR->>Scribe: POST /session (Start Session)
    Scribe-->>EMR: 201 Created (Session ID)
    
    loop Recording
        EMR->>Scribe: POST /session/{id}/audio (Chunk N)
        Scribe-->>EMR: 200 OK
    end
    
    EMR->>Scribe: POST /session/{id}/commit (Finalize)
    Scribe-->>EMR: 202 Accepted (Job ID)
    
    opt Retrieval via Polling
        loop Until Done
            EMR->>Scribe: GET /session/{id}/result
            Scribe-->>EMR: 200 OK (Status: Processing)
        end
        EMR->>Scribe: GET /session/{id}/result
        Scribe-->>EMR: 200 OK (Final Output)
    end
```

## Security Model

*   **Transport Security**: All communication MUST happen over HTTPS (TLS 1.2+).
*   **Authentication**:
    *   Standard `Authorization` header.
    *   Supports Bearer Tokens (OAuth2) or API Keys (`Authorization: Bearer <token>`).
    *   Scribe vendors provide credentials to EMR integrators.

## Data Exchange
*   **Format**: JSON for all control messages and metadata.
*   **Audio**: Common formats (WAV, MP3, AAC, M4A).
*   **Encoding**: Base64 for small inline audio, or standard multipart/form-data for uploads.
