# Usage guide

## Before you begin

Use a non-production Confluence space for evaluation. Confirm that your deployment permits HTML
macros and supports the REST operations in [API reference](api-reference.md). The authenticated
account needs permission to read and edit every page in the batch.

Install the package in an isolated environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configure a session

Set the base URL and username in your shell. Set the API token the same way, or omit it and enter it
at the hidden prompt.

```bash
export CONFLUENCE_BASE_URL="https://docs.example.com/confluence"
export CONFLUENCE_USERNAME="portfolio-user"
export CONFLUENCE_API_TOKEN="<set-locally>"
```

Do not put real credentials in `.env.example`, CSV files, terminal screenshots, or commits. The
included `.gitignore` excludes a local `.env` file, but this package does not load that file
automatically.

Global options must appear before the `add` or `remove` command.

| Option | Meaning |
| --- | --- |
| `--base-url URL` | Override `CONFLUENCE_BASE_URL` for this run |
| `--username NAME` | Override `CONFLUENCE_USERNAME` for this run |
| `--timeout SECONDS` | Set the HTTP timeout; default is 30 seconds |
| `--dry-run` | Read and validate pages without calling write endpoints |
| `--yes` | Bypass the final confirmation for an intentional unattended run |
| `--debug` | Enable local diagnostic logging; secrets and bodies remain excluded |

## Add one redirect

Start with a dry run:

```bash
confluence-toolkit --dry-run add \
  --page-id 10001 \
  --target-url "https://kb.example.com/articles/reset-demo-password" \
  --target-title "Reset a demo password"
```

Remove `--dry-run` only after reviewing the plan. The confirmation prompt defaults to `no`.

```bash
confluence-toolkit add \
  --page-id 10001 \
  --target-url "https://kb.example.com/articles/reset-demo-password" \
  --target-title "Reset a demo password"
```

## Add a CSV batch

Use UTF-8 CSV with these required columns:

```csv
page_id,target_url,target_title
10001,https://kb.example.com/articles/reset-demo-password,Reset a demo password
10002,https://kb.example.com/articles/request-demo-access,Request demo access
```

Quoted CSV fields are supported. Empty required values, non-HTTP(S) targets, or a header-only file
stop the run before any page writes begin.

```bash
confluence-toolkit --dry-run add --csv examples/sample-input.csv
confluence-toolkit add --csv examples/sample-input.csv
```

For automation that has a separate approval control, `--yes` skips the interactive prompt:

```bash
confluence-toolkit --yes add --csv examples/sample-input.csv
```

## Remove redirects

The remove operation recognizes only markup created by this public sample.

```bash
confluence-toolkit --dry-run remove --page-id 10001
confluence-toolkit remove --page-id 10001
```

For a batch, supply a CSV containing `page_id`:

```bash
confluence-toolkit --dry-run remove --csv examples/sample-remove.csv
```

## Interpret results

| State | Meaning |
| --- | --- |
| `planned` | Dry run validated the page and calculated the proposed change; nothing was written |
| `changed` | The page update succeeded; any label problem appears as a warning |
| `skipped` | The requested end state already existed or no managed redirect was found |
| `failed` | The page-level operation could not complete; remaining batch records continue |

The process exits with `0` when every result is planned, changed, or skipped; `1` when one or more
page operations fail; `2` for configuration or input errors; and `130` after an interrupt.

See [sample-output.txt](../examples/sample-output.txt) for representative output generated with
dummy identifiers and domains.

## Troubleshooting

### HTTP 401 or 403

Confirm the username/token pair and page permissions. The client uses HTTP Basic authentication;
adapt the transport layer if your deployment requires a different scheme.

### HTTP 409 or a version conflict

Another editor may have changed the page after it was fetched. Re-run the command so the client
reads the current body and version. Do not manually force the stale version number.

### The page changed but its label did not

The content write and label request are separate API calls. The tool reports the label error as a
warning while retaining the successful page result. Use the page version history and warning text
to reconcile the label.

### No redirect was removed

The removal pattern is intentionally narrow. It ignores unrelated HTML macros and redirects that
do not contain this sample's marker. Inspect the page storage format before extending the pattern.

### HTML macros are disabled

Some Confluence deployments restrict HTML macros. This sample cannot bypass that policy. Use a
permitted redirect mechanism or adapt the content transformation after administrator review.
