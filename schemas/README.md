# JSON Schemas

This directory will contain JSON Schema definitions for protocol validation.

## Planned Schemas

| Schema | Description | Status |
|--------|-------------|--------|
| `discovery.schema.json` | Discovery document validation | Planned |
| `session-request.schema.json` | Session creation request | Planned |
| `session-response.schema.json` | Session response | Planned |
| `webhook-payload.schema.json` | Webhook payload validation | Planned |
| `error.schema.json` | Error response validation | Planned |

## Template Output Schemas

| Schema | Description | Status |
|--------|-------------|--------|
| `templates/soap.schema.json` | SOAP note output | Planned |
| `templates/medications.schema.json` | Medications list output | Planned |
| `templates/transcript.schema.json` | Transcript output | Planned |

## Contributing

To contribute schemas:

1. Use JSON Schema Draft 2020-12
2. Include descriptions for all properties
3. Provide examples
4. Test against example payloads

## Usage

```javascript
const Ajv = require('ajv');
const ajv = new Ajv();

const discoverySchema = require('./discovery.schema.json');
const validate = ajv.compile(discoverySchema);

const discoveryDoc = await fetch('/.well-known/medscribealliance').then(r => r.json());

if (validate(discoveryDoc)) {
  console.log('Valid discovery document');
} else {
  console.log('Validation errors:', validate.errors);
}
```
