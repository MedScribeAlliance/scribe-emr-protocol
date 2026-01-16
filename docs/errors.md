# Error Catalog

SEP uses standard HTTP status codes to indicate success or failure. The body of a 4xx/5xx response will typically contain a structured `Error` object.

```json
{
  "code": "resource_not_found",
  "message": "The session ID 'sess_123' does not exist.",
  "request_id": "req_abc987"
}
```

## Common Error Codes

| Status | Error Code | Description | Recovery Action |
| :--- | :--- | :--- | :--- |
| **400** | `validation_error` | The request body is missing required fields or has invalid types. | Fix the payload logic in the EMR. Do not retry. |
| **400** | `audio_unsupported` | The file format is not supported (e.g., `.flac` when only `.mp3` is allowed). | Transcode audio to a supported format on the client. |
| **401** | `unauthorized` | Missing or invalid API token. | Check credentials. If OAuth, refresh the token. |
| **403** | `forbidden` | Token is valid but permissions are lacking. | Contact the Scribe administrator. |
| **404** | `resource_not_found` | Job, Session, or Template ID not found. | Verify IDs. If Template is missing, refresh Discovery. |
| **429** | `rate_limit_exceeded` | Too many requests in a short window. | **Retry** after the duration specified in `Retry-After` header. |
| **500** | `internal_error` | Scribe server crashed. | **Retry** with exponential backoff. |
| **503** | `service_unavailable` | Scribe is under maintenance. | **Retry** later. |

## Domain-Specific Errors

### Transcription Failures
Sometimes the job accepts successfully (202) but fails later. This is reported via Webhook with `status: "failed"`.

| Error Code | Meaning | Action |
| :--- | :--- | :--- |
| `audio_quality_low` | Too much background noise; unintelligible. | Prompt user to re-record in a quiet environment. |
| `audio_too_short` | File was empty or < 1s. | Check audio capture logic. |
| `processing_timeout` | AI model took too long. | Retry once. If persistent, contact support. |
