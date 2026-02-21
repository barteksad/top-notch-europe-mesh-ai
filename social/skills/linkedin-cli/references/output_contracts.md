# LinkedIn CLI Output Contracts

These contracts define stable payloads for machine consumers.

## 1) Post Receipt Contract (`post create`)

Top-level fields:
- `status`: `ok` or `error`
- `operation`: `post.create`
- `profile`: active profile name
- `dry_run`: boolean
- `timestamp`: ISO-8601 UTC
- `request`: normalized publish request body
- `receipt`: created-post metadata
- `ledger`: persisted local event metadata

`receipt` fields:
- `post_urn`: URN from LinkedIn response when available
- `post_url`: derived feed URL when URN can be mapped
- `author_urn`
- `visibility`: `PUBLIC` or `CONNECTIONS`
- `lifecycle_state`: typically `PUBLISHED`
- `request_id`: request trace header if returned (`x-linkedin-request-id`)
- `restli_id`: value from `x-restli-id` when returned
- `http_status`: HTTP status code
- `api_response`: parsed JSON response body (or `null`)
- `response_headers`: selected response headers
- `created_at`: ISO-8601 UTC timestamp

`ledger` fields:
- `event_id`: deterministic local event id
- `path`: absolute or relative ledger path

## 2) Post Detail Contract (`post get`)

Top-level fields:
- `status`
- `operation`: `post.get`
- `profile`
- `post_urn`
- `remote`: object or `null`
- `history`: zero-or-more matching ledger entries

`remote` fields:
- `http_status`
- `headers`
- `body`

## 3) Post List Contract (`post list`)

Top-level fields:
- `status`
- `operation`: `post.list`
- `profile`
- `author_urn`
- `remote`: list payload from LinkedIn (`elements`, paging)
- `history`: local ledger subset

## 4) Analytics Contract (`analytics get`)

Top-level fields:
- `status`
- `operation`: `analytics.get`
- `profile`
- `post_urn`
- `collected_at`
- `engagement`
- `raw`

`engagement` normalized fields:
- `likes`
- `comments`
- `shares` (nullable if not available)
- `reactions` (nullable if not available)

## 5) Error Contract

For `--json`, errors should be:

```json
{
  "status": "error",
  "error": {
    "code": 5,
    "message": "Missing LinkedIn access token",
    "details": {}
  }
}
```

For `--plain`, errors should be:

```text
error.code=5
error.message=Missing LinkedIn access token
```

## 6) Schema Files

Use bundled schemas for automated checks:
- `assets/contracts/post_receipt.schema.json`
- `assets/contracts/post_analytics.schema.json`
