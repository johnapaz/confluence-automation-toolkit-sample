# API reference

This reference describes the public sample's Python surface and the Confluence REST operations it
calls. It is intentionally limited to behavior present in this repository.

## REST operations

The configured `CONFLUENCE_BASE_URL` is prepended to every path.

| Method | Path | Purpose | Expected success |
| --- | --- | --- | --- |
| `GET` | `/rest/api/space?limit=1` | Verify connectivity and authentication | `200` |
| `GET` | `/rest/api/content/{page_id}?expand=body.storage,version` | Fetch the current title, storage body, and version | `200` |
| `PUT` | `/rest/api/content/{page_id}` | Create the next page version with updated storage content | `200` or `201` |
| `POST` | `/rest/api/content/{page_id}/label` | Apply the `redirected` tracking label | `200`, `201`, or `204` |
| `DELETE` | `/rest/api/content/{page_id}/label/{label}` | Remove the tracking label | `200`, `204`, or `404` |

`page_id` and `label` path segments are URL-encoded. The client supplies a 30-second timeout by
default and converts transport, status, and JSON-shape failures into `ApiError`.

### Page update body

```json
{
  "version": {
    "number": 8,
    "minorEdit": true,
    "message": "Added redirect to Reset a demo password"
  },
  "title": "Reset a demo password",
  "type": "page",
  "body": {
    "storage": {
      "value": "<ac:structured-macro>...</ac:structured-macro>",
      "representation": "storage"
    }
  }
}
```

The example uses dummy data. The actual storage value includes the managed redirect followed by
the page's existing storage body.

## Python interfaces

### `ConfluenceClient`

```python
ConfluenceClient(
    base_url: str,
    username: str,
    api_token: str,
    *,
    timeout: float = 30.0,
    session: requests.Session | None = None,
)
```

The optional session supports offline tests and controlled transport customization.

| Method | Returns | Notes |
| --- | --- | --- |
| `test_connection()` | `None` | Raises `ApiError` on failure |
| `get_page(page_id)` | `PageSnapshot` | Requires `id`, `title`, `body.storage.value`, and `version.number` |
| `update_page(page, storage_value, version_comment)` | `int` | Sends `page.version + 1`; returns the server version when present |
| `add_label(page_id, label)` | `None` | Called only after a successful content update |
| `remove_label(page_id, label)` | `None` | Treats a missing label (`404`) as the requested end state |

### `RedirectService`

```python
RedirectService(client: ConfluenceClient, *, label: str = "redirected")
```

`add(request, dry_run=False)` and `remove(page_id, dry_run=False)` each return an
`OperationResult`. They normalize page-level exceptions into a `failed` result so batch processing
can continue.

### Data contracts

```python
PageSnapshot(page_id: str, title: str, storage_value: str, version: int)
RedirectRequest(page_id: str, target_url: str, target_title: str, source_row: int | None)
OperationResult(
    page_id: str,
    page_title: str,
    action: Literal["add", "remove"],
    status: Literal["changed", "skipped", "planned", "failed"],
    message: str,
    previous_version: int | None,
    new_version: int | None,
    warnings: tuple[str, ...],
)
```

### CSV functions

- `parse_redirect_csv(path)` validates and returns add requests from
  `page_id,target_url,target_title` rows.
- `parse_page_id_csv(path)` validates and returns page IDs from `page_id` rows.
- `validate_target_url(value)` accepts only absolute `http` or `https` URLs.

## Error model

| Error | Boundary | Typical cause |
| --- | --- | --- |
| `ConfigurationError` | CLI/client initialization | Missing base URL, username, or token; invalid URL scheme |
| `InputError` | CSV/content validation | Missing columns or values, empty file, unsafe destination scheme |
| `ApiError` | REST transport and response handling | Network failure, non-success status, or unexpected response shape |

The client intentionally omits response bodies from error messages because those bodies may
contain page or infrastructure details. When available, an upstream request ID is retained for
support investigation.
