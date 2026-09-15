# Confluence Automation Toolkit — Portfolio Sample

> **Portfolio notice:** This repository is a sanitized portfolio reconstruction of internal
> documentation automation tooling I developed in a previous role. It contains no production
> credentials, proprietary data, internal URLs, or employer source files.

This project demonstrates how I turned a high-volume documentation migration into a controlled,
repeatable workflow. The original assignment required thousands of changes across Confluence.
Performing those changes manually through the UI would have consumed hundreds of hours and made
results difficult to verify.

I began with a focused permission-management script, then developed a family of Python utilities
for redirect management, macro cleanup, find-and-replace operations, permissions, and migration
reporting. Six teammates ultimately relied on those tools. Collectively, they saved hundreds of
hours and helped the team complete the migration ahead of schedule.

This repository presents one coherent, portfolio-safe slice of that work: a CLI for adding and
removing page redirects through the Confluence REST API.

## What the sample demonstrates

- Version-aware REST API reads and writes
- Single-page and CSV batch processing
- Preview and explicit confirmation before writes
- A dry-run path that performs no mutation
- Minor-edit flags and version comments for traceability
- A tracking label for finding changed pages
- Per-page results so one failure does not hide the rest of a batch
- Reversible changes that preserve the original page body
- Runtime-only credentials and diagnostics that omit credentials and page bodies
- Typed boundaries between the CLI, service layer, and API client

The target system is intentionally generic. Operators provide complete destination URLs; no
former employer routing rules, hostnames, identifiers, or business logic remain.

## Quick start

Requirements: Python 3.10+ and access to a Confluence instance that supports the REST endpoints
documented in [API reference](docs/api-reference.md).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

export CONFLUENCE_BASE_URL="https://docs.example.com/confluence"
export CONFLUENCE_USERNAME="portfolio-user"
export CONFLUENCE_API_TOKEN="<set-locally>"

confluence-toolkit --dry-run add --csv examples/sample-input.csv
```

The tool prompts for an API token when `CONFLUENCE_API_TOKEN` is unset. It does not write
credentials to disk or include them in debug messages.

To run the automated checks:

```bash
pip install -e '.[dev]'
pytest
ruff check .
```

## Safety model

Every write follows the same sequence:

1. Validate the input record and destination URL.
2. Fetch the latest page body and version.
3. Build a proposed next version without discarding the existing body.
4. Stop after reporting the plan when `--dry-run` is active.
5. Require confirmation unless the operator deliberately passes `--yes`.
6. Write a minor edit with a human-readable version comment.
7. Add or remove a tracking label and report label failures separately.

Removal targets only redirect markup carrying this sample's management marker. It does not delete
unrelated HTML macros.

## Documentation

- [Usage guide](docs/usage.md) — configuration, commands, CSV contracts, and troubleshooting
- [Architecture](docs/architecture.md) — components, data flow, and design decisions
- [API reference](docs/api-reference.md) — REST calls, Python interfaces, and result states
- [Portfolio note](PORTFOLIO-NOTE.md) — provenance, sanitization, AI-assisted development, and scope
- [Publication checklist](docs/publication-checklist.md) — final owner review before public release

## Repository structure

```text
.
├── docs/                      # Task, architecture, API, and review documentation
├── examples/                  # Dummy CSV input and representative console output
├── src/confluence_toolkit/    # CLI, REST client, models, and redirect service
├── tests/                     # Offline unit tests; no Confluence access required
├── .env.example               # Empty local configuration template
├── PORTFOLIO-NOTE.md          # Context and disclosure
└── pyproject.toml             # Package metadata and development tooling
```

## Development approach

I used AI-assisted coding during the original project as an implementation accelerator. I defined
the operational problem and requirements, selected the workflows, reviewed generated changes,
tested behavior against real scenarios, documented usage, and kept working versions under Git so
new changes could be evaluated without breaking established tools.

The same accountability applies here: AI assistance does not replace product judgment, source
review, testing, security review, or authorship of the documentation strategy.

## Scope and limitations

This is an executable portfolio sample, not a supported production package. Confluence Cloud and
Server/Data Center deployments differ in authentication, storage-format behavior, HTML macro
policy, and minor-edit support. Review the API contract and test against a non-production space
before adapting this code.

No license is included. The repository owner should select one only after confirming the rights and
distribution terms appropriate for this reconstruction.
