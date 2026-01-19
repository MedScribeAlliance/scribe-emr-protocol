# 5. Authentication & Authorization

**MedScribeAlliance Protocol Specification v0.1**

---

The protocol supports two authentication mechanisms to address different integration patterns:

| Method | Use Case | Billing Relationship |
|--------|----------|---------------------|
| **API Key** | B2B - EMR integrates directly | Scribe → EMR |
| **OIDC** | B2C - Users authenticate directly | Scribe → User |

Scribe Services MUST support at least one method. MAY support both.

---

## 5.1 API Key Authentication (B2B)

For direct EMR-to-Scribe integrations where the EMR is the billable customer.

### Request Format

Include the API key in the `X-API-Key` header:

```http
GET /sessions/abc123 HTTP/1.1
Host: api.scribe.example.com
X-API-Key: sk_live_abc123def456ghi789
Content-Type: application/json
```

### Key Format

API keys SHOULD follow this convention:

| Prefix | Environment | Example |
|--------|-------------|---------|
| `sk_live_` | Production | `sk_live_abc123def456...` |
| `sk_test_` | Testing/Sandbox | `sk_test_xyz789abc123...` |

### Key Management Requirements

**Scribe Services MUST:**

- Provide secure key generation mechanism
- Support key rotation without downtime
- Allow multiple active keys per EMR client
- Log key usage for auditing

**EMR Clients MUST:**

- Store keys securely (environment variables, secrets manager)
- Never expose keys in client-side code
- Never include keys in URLs or query parameters
- Rotate keys periodically

### Error Responses

#### Missing API Key

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": {
    "code": "authentication_failed",
    "message": "API key is required"
  }
}
```

#### Invalid API Key

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": {
    "code": "authentication_failed",
    "message": "Invalid API key"
  }
}
```

---

## 5.2 OIDC Authentication (B2C)

For user-authorized integrations where users authenticate directly with the Scribe Service.

### Supported Flows

| Flow | Use Case |
|------|----------|
| Authorization Code + PKCE | Web applications, mobile apps, SPAs |

Client Credentials flow is NOT used for B2C; use API Keys for backend-to-backend calls.

### Authorization Code Flow with PKCE

#### Step 1: Generate Code Verifier and Challenge

EMR client generates PKCE parameters:

```javascript
// Generate random code verifier (43-128 characters)
const codeVerifier = generateRandomString(64);

// Generate code challenge (SHA256 hash, base64url encoded)
const codeChallenge = base64url(sha256(codeVerifier));
```

#### Step 2: Redirect to Authorization Endpoint

EMR redirects user to Scribe's authorization endpoint:

```
GET https://auth.scribe.example.com/oauth/authorize
  ?response_type=code
  &client_id=emr_client_id
  &redirect_uri=https://emr.example.com/callback
  &scope=openid profile
  &state=random_state_value
  &code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
  &code_challenge_method=S256
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `response_type` | Yes | Must be `code` |
| `client_id` | Yes | EMR's registered client ID |
| `redirect_uri` | Yes | Callback URL (must be pre-registered) |
| `scope` | Yes | `openid profile` minimum |
| `state` | Yes | Random value for CSRF protection |
| `code_challenge` | Yes | PKCE code challenge |
| `code_challenge_method` | Yes | Must be `S256` |

#### Step 3: User Authenticates

User authenticates with Scribe Service (login form, SSO, etc.)

#### Step 4: Receive Authorization Code

Scribe redirects back to EMR with authorization code:

```
GET https://emr.example.com/callback
  ?code=authorization_code_here
  &state=random_state_value
```

EMR MUST verify `state` matches the original value.

#### Step 5: Exchange Code for Tokens

EMR backend exchanges code for tokens:

```http
POST /oauth/token HTTP/1.1
Host: auth.scribe.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code
&code=authorization_code_here
&redirect_uri=https://emr.example.com/callback
&client_id=emr_client_id
&code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

#### Step 6: Receive Tokens

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here",
  "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Step 7: Use Access Token

```http
GET /sessions/abc123 HTTP/1.1
Host: api.scribe.example.com
Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 5.3 Token Refresh

Access tokens have limited lifetime. EMR clients MUST implement token refresh.

### Refresh Request

```http
POST /oauth/token HTTP/1.1
Host: auth.scribe.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token=refresh_token_here
&client_id=emr_client_id
```

### Refresh Response

```json
{
  "access_token": "new_access_token_here",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "new_refresh_token_here"
}
```

### Token Refresh Best Practices

- Refresh tokens before expiry (e.g., when 80% of lifetime elapsed)
- Handle refresh failures gracefully (re-authenticate user)
- Store refresh tokens securely
- Implement token refresh as background process

---

## 5.4 Authentication Selection

EMR clients should select authentication method based on integration pattern:

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Is the EMR the billable customer?                     │
│                                                         │
│           YES                         NO                │
│            │                           │                │
│            ▼                           ▼                │
│   ┌─────────────────┐       ┌─────────────────┐        │
│   │   Use API Key   │       │   Use OIDC      │        │
│   │                 │       │                 │        │
│   │  • X-API-Key    │       │  • Auth Code    │        │
│   │  • Backend only │       │  • PKCE         │        │
│   │  • EMR manages  │       │  • User auth    │        │
│   │    users        │       │  • Direct       │        │
│   │                 │       │    billing      │        │
│   └─────────────────┘       └─────────────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 5.5 Security Requirements

### For Scribe Services

- MUST validate all tokens/keys on every request
- MUST use secure token storage
- MUST implement rate limiting per client/user
- SHOULD implement anomaly detection
- SHOULD log authentication events

### For EMR Clients

- MUST store credentials securely
- MUST use HTTPS for all requests
- MUST implement PKCE for OIDC flows
- MUST validate `state` parameter
- SHOULD implement token caching with secure storage

---

**Previous:** [Discovery](./04-discovery.md) | **Next:** [Sessions](./06-sessions.md)
