# 4. Discovery

**MedScribeAlliance Protocol Specification v0.1**

---

## 4.1 Well-Known Endpoint

Scribe Services MUST publish a discovery document at:

```
GET /.well-known/medscribealliance
```

### Requirements

- This endpoint MUST be publicly accessible without authentication
- Response MUST be `Content-Type: application/json`
- Response SHOULD be cacheable (recommended: `Cache-Control: max-age=3600`)

### Example Request

```http
GET /.well-known/medscribealliance HTTP/1.1
Host: scribe.example.com
Accept: application/json
```

### Example Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Cache-Control: max-age=3600

{
  "protocol": "medscribealliance",
  "protocol_version": "0.1",
  ...
}
```

## 4.2 Discovery Document Schema

```json
{
  "protocol": "medscribealliance",
  "protocol_version": "0.1",
  "supported_versions": ["0.1"],
  
  "service": {
    "name": "Example Scribe Service",
    "documentation_url": "https://docs.example.com/scribe",
    "support_email": "support@example.com"
  },
  
  "endpoints": {
    "base_url": "https://api.scribe.example.com/v1",
    "webhooks_url": "https://api.scribe.example.com/v1/webhooks"
  },
  
  "authentication": {
    "supported_methods": ["api_key", "oidc"],
    "oidc": {
      "issuer": "https://auth.scribe.example.com",
      "authorization_endpoint": "https://auth.scribe.example.com/oauth/authorize",
      "token_endpoint": "https://auth.scribe.example.com/oauth/token"
      "scopes_supported": ["openid", "profile"]
    }
  },
  
  "capabilities": {
    "audio_formats": [
      "audio/webm;codecs=opus",
      "audio/wav",
      "audio/ogg"
    ],
    "max_chunk_duration_seconds": 20,
    "upload_methods": ["chunked", "single"],
    "webhook_delivery": true,
    "client_sdk_delivery": true
  },
  
  "models": [
    {
      "id": "lite",
      "display_name": "Lite",
      "languages": ["en", "hi"],
      "max_session_duration_seconds": 600,
      "response_speed": "fast",
      "features": {
        "realtime_transcription": false,
        "speaker_diarization": false,
        "custom_templates": false
      }
    },
    {
      "id": "pro",
      "display_name": "Professional",
      "languages": ["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"],
      "max_session_duration_seconds": 3600,
      "response_speed": "standard",
      "features": {
        "realtime_transcription": true,
        "speaker_diarization": true,
        "custom_templates": true
      }
    }
  ],
  
  "languages": {
    "supported": ["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"],
    "auto_detection": true
  }
}
```

## 4.3 Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `protocol` | string | MUST be `"medscribealliance"` |
| `protocol_version` | string | Current protocol version (e.g., `"0.1"`) |
| `supported_versions` | array | All supported protocol versions |
| `endpoints.base_url` | string | Base URL for API endpoints |
| `endpoints.webhooks_url` | string | Webhook registration endpoint (if webhook delivery supported) |
| `authentication.supported_methods` | array | Supported auth methods: `["api_key"]`, `["oidc"]`, or both |
| `capabilities.audio_formats` | array | Supported audio MIME types |
| `capabilities.max_chunk_duration_seconds` | integer | Maximum audio chunk duration (≤20 recommended) |
| `models` | array | Available model configurations |

## 4.4 Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `service.name` | string | Human-readable service name |
| `service.documentation_url` | string | Link to service documentation |
| `service.support_email` | string | Support contact email |
| `endpoints.authorization_endpoint` | string | OIDC authorization URL (required if OIDC supported) |
| `endpoints.token_endpoint` | string | OIDC token URL (required if OIDC supported) |
| `authentication.oidc` | object | OIDC-specific configuration |
| `capabilities.upload_methods` | array | `["chunked"]`, `["single"]`, or both |
| `capabilities.webhook_delivery` | boolean | Whether webhook delivery is supported |
| `capabilities.client_sdk_delivery` | boolean | Whether client SDK delivery is supported |
| `languages.auto_detection` | boolean | Whether automatic language detection is supported |

## 4.5 Model Configuration

Each model in the `models` array describes a service tier:

```json
{
  "id": "pro",
  "display_name": "Professional",
  "languages": ["en", "hi", "ta", "te"],
  "max_session_duration_seconds": 3600,
  "response_speed": "standard",
  "features": {
    "realtime_transcription": true,
    "speaker_diarization": true,
    "custom_templates": true
  }
}
```

### Model Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique model identifier used in API calls |
| `display_name` | string | Yes | Human-readable name |
| `languages` | array | Yes | ISO 639-1 language codes supported |
| `max_session_duration_seconds` | integer | Yes | Maximum session length allowed |
| `response_speed` | string | No | Processing speed: `"fast"`, `"standard"`, `"thorough"` |
| `features` | object | No | Feature availability flags |

### Response Speed

| Value | Description |
|-------|-------------|
| `fast` | Optimized for speed, may trade off accuracy |
| `standard` | Balanced speed and accuracy |
| `thorough` | Optimized for accuracy, may take longer |

### Feature Flags

| Feature | Description |
|---------|-------------|
| `realtime_transcription` | Live transcription during recording |
| `speaker_diarization` | Automatic speaker identification |
| `custom_templates` | Support for custom template creation |

## 4.6 Language Support

```json
{
  "languages": {
    "supported": ["en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"],
    "auto_detection": true
  }
}
```

### Supported Indian Languages

| Code | Language |
|------|----------|
| `en` | English |
| `hi` | Hindi |
| `ta` | Tamil |
| `te` | Telugu |
| `bn` | Bengali |
| `mr` | Marathi |
| `gu` | Gujarati |
| `kn` | Kannada |
| `ml` | Malayalam |
| `pa` | Punjabi |

## 4.7 Audio Format Specification

Audio formats use MIME type notation:

| Format | MIME Type | Notes |
|--------|-----------|-------|
| WebM Opus | `audio/webm;codecs=opus` | Recommended for browser capture |
| WAV | `audio/wav` | Uncompressed, larger files |
| OGG | `audio/ogg` | Good compression |
| OGG Opus | `audio/ogg;codecs=opus` | Good compression with Opus |

### Recommended Encoding

- Sample rate: 16kHz or higher
- Channels: Mono (1 channel) preferred
- Bit depth: 16-bit for WAV

## 4.8 Discovery Caching

EMR clients SHOULD cache the discovery document to reduce latency:

- Recommended cache duration: 1 hour
- Respect `Cache-Control` headers if provided
- Re-fetch on authentication errors or unexpected responses

---

**Previous:** [Versioning](./03-versioning.md) | **Next:** [Authentication](./05-authentication.md)
