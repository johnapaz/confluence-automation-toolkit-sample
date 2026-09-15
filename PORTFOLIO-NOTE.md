# Portfolio note

## What this repository is

This repository is a sanitized reconstruction of documentation-operations tooling I designed and
maintained during a large Confluence migration. It demonstrates representative architecture,
workflows, safety controls, and documentation practices without publishing internal source code.

The executable subset focuses on redirect management because that utility provides a compact view
of the broader work: REST API integration, interactive and batch workflows, reversible content
changes, status feedback, authentication boundaries, error handling, and version-based
auditability.

## What the original tool family included

The source material reviewed for this reconstruction contained four related utilities:

- a space metrics reporter that inventoried page hierarchy, macros, and attachments in Excel;
- a targeted find-and-replace utility for removing obsolete page sections;
- a Jira macro cleanup utility that detected and removed macros with empty parameters; and
- a redirect manager that added and removed redirects individually or from CSV batches.

The tools shared a Python REST client, interactive CLI patterns, credential handling, debug output,
progress reporting, confirmation steps, and per-operation feedback. Later utilities retained parts
of earlier projects, so the archive set represented an evolving tool family rather than four
entirely independent codebases.

## Sanitization and reconstruction

The public version excludes or generalizes:

- employer and internal team names;
- production, development, source-control, and destination-system domains;
- internal project keys, page IDs, solution IDs, labels, and sample records;
- destination-specific URL construction and migration taxonomy;
- internal authentication terminology and network assumptions;
- duplicate or superseded modules carried between tool iterations; and
- any credentials, tokens, page bodies, employee names, or production exports.

Examples use reserved `example.com` domains and invented identifiers. Runtime configuration
replaces hard-coded environments. The package was rewritten around the verified behavior of the
original tools; it is not a verbatim copy with strings deleted.

The reconstruction also narrows redirect removal to markup carrying an explicit management marker
and keeps credentials runtime-only. Those choices make the public example safer and clearer while
preserving the original add/remove, dry-run, confirmation, version-comment, labeling, batch, and
feedback patterns.

## Authorship and AI assistance

I used AI-assisted coding as part of the original implementation workflow. My responsibilities
included:

- identifying the operational bottleneck and defining product requirements;
- choosing where automation was appropriate and where human confirmation was required;
- designing operator flows, messages, safeguards, and recovery paths;
- reviewing and testing generated code against migration scenarios;
- using Git to protect working versions while capabilities evolved; and
- documenting setup and usage so colleagues could reproduce the work.

For this portfolio reconstruction, AI assistance was also used to inspect, sanitize, refactor,
test, and document the sample under my direction. The repository is intended to show technical
communication, systems thinking, API fluency, and responsible tool stewardship—not to present me
as a full-time software engineer.

## Impact and claim boundaries

Six colleagues relied on the original family of tools. Across that family, the automation saved
hundreds of hours of manual work and helped the team complete the migration assignment ahead of
schedule. Those outcomes describe the internal toolset as a whole, not a benchmark of this public
redirect subset.

No former employer endorses or maintains this repository.
