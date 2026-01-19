# 3. Protocol Versioning

**MedScribeAlliance Protocol Specification v0.1**

---

## 3.1 Version Format

Protocol versions follow semantic versioning: `MAJOR.MINOR`

| Component | Description | Example |
|-----------|-------------|---------|
| **MAJOR** | Breaking changes that require client updates | `1.0` → `2.0` |
| **MINOR** | Backward-compatible additions | `1.0` → `1.1` |

### Version Examples

- `0.1` - Initial draft specification
- `0.2` - Added streaming support (backward compatible)
- `1.0` - First stable release
- `2.0` - Breaking changes to session API

## 3.2 Version Declaration

The discovery document declares supported protocol versions:

```json
{
  "protocol": "medscribealliance",
  "protocol_version": "0.1",
  "supported_versions": ["0.1"]
}
```

| Field | Description |
|-------|-------------|
| `protocol_version` | Current/primary version implemented |
| `supported_versions` | Array of all supported versions |

## 3.3 Version Negotiation

### EMR Client Request

EMR clients SHOULD specify desired protocol version in requests via the `MSA-Version` header:

```http
GET /sessions/abc123
Authorization: X-API-Key sk_live_xxx
MSA-Version: 0.1
```

### Scribe Service Response

If the requested version is supported, the Scribe Service processes the request accordingly.

If the requested version is NOT supported, the Scribe Service SHOULD return:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": {
    "code": "unsupported_version",
    "message": "Protocol version 0.2 is not supported",
    "details": {
      "requested_version": "0.2",
      "supported_versions": ["0.1", "1.0"]
    }
  }
}
```

### Default Behavior

If no `MSA-Version` header is provided:

- Scribe Service SHOULD use the latest stable version
- Scribe Service MAY use `protocol_version` from discovery document

## 3.4 Backward Compatibility

### Scribe Service Requirements

- MUST support at least the current major version
- SHOULD support previous major version for 12 months after deprecation announcement
- MUST declare all supported versions in discovery document
- MUST NOT remove endpoints without major version bump

### EMR Client Recommendations

- SHOULD specify desired protocol version in requests
- SHOULD check discovery document for supported versions before integration
- MUST handle graceful degradation if requested version is unsupported
- SHOULD implement version-specific logic if supporting multiple versions

## 3.5 Deprecation Policy

### Announcing Deprecation

Scribe Services SHOULD announce deprecation in the discovery document:

```json
{
  "protocol_version": "1.0",
  "supported_versions": ["0.1", "1.0"],
  "deprecated_versions": [
    {
      "version": "0.1",
      "sunset_date": "2026-01-01",
      "migration_guide": "https://docs.example.com/migrate-0.1-to-1.0"
    }
  ]
}
```

### Deprecation Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| Announcement | - | Add to `deprecated_versions` |
| Warning Period | 6 months | Return `X-MSA-Deprecated: true` header |
| Sunset | 12 months from announcement | Version removed from `supported_versions` |

### Deprecation Header

During the warning period, responses to deprecated version requests SHOULD include:

```http
HTTP/1.1 200 OK
X-MSA-Deprecated: true
X-MSA-Sunset-Date: 2026-01-01
```

## 3.6 Version Changelog

Scribe Services SHOULD maintain a changelog accessible via the discovery document:

```json
{
  "service": {
    "changelog_url": "https://docs.example.com/changelog"
  }
}
```

---

**Previous:** [Architecture](./02-architecture.md) | **Next:** [Discovery](./04-discovery.md)
