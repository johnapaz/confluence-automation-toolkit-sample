# Portfolio note

## What this repository is

This repository is a sanitized reconstruction of documentation-operations tooling John Paz
designed and maintained while working as a contract technical writer supporting Airbnb during a
large Confluence migration.

The public subset focuses on redirect management because it provides a compact view of the broader
work: REST API integration, interactive and batch workflows, reversible content changes, status
feedback, authentication boundaries, error handling, and version-based auditability.

It is a portfolio case study—not the original internal source, a supported product, or a claim that
John personally authored every line of the current package.

Airbnb did not sponsor, review, or endorse this repository.

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

## Original authorship and AI assistance

John identified the operational bottleneck, defined the product requirements, selected the
workflows, designed the operator experience and safeguards, directed AI-assisted implementation,
reviewed and tested changes against real migration scenarios, maintained working versions in Git,
documented setup and use, and supported the colleagues who relied on the tools.

That is the work this case study is intended to demonstrate: technical communication, systems
thinking, API fluency, operator advocacy, and responsible stewardship of AI-assisted software.

## Public reconstruction

John supplied the original source archives, explained their history and use, chose the portfolio
goal, and defined the confidentiality and accuracy constraints. OpenAI Codex then inspected the
archives and produced much of this public package's sanitization, refactoring, tests,
documentation, and presentation under John's direction.

John has not manually authored or independently validated every line of the reconstructed package.
The public code has offline automated tests, but it has not been integration-tested against a live
Confluence environment. Its executable form demonstrates the original patterns; it does not prove
that this exact package is production-ready.

See [CONTRIBUTIONS.md](CONTRIBUTIONS.md) for the explicit contribution boundary.

## Sanitization

The public version excludes or generalizes:

- internal team names;
- production, development, source-control, and destination-system domains;
- internal project keys, page IDs, solution IDs, labels, and sample records;
- destination-specific URL construction and migration taxonomy;
- internal authentication terminology and network assumptions;
- duplicate or superseded modules carried between tool iterations; and
- credentials, tokens, page bodies, employee names, and production exports.

Examples use reserved `example.com` domains and invented identifiers. Runtime configuration
replaces hard-coded environments. The package was rewritten around verified behaviors of the
original tools; it is not a verbatim copy with sensitive strings deleted.

## Impact and claim boundaries

Six colleagues relied on the original family of tools. Across that family, the automation saved
hundreds of hours of manual work and helped the team complete the migration assignment ahead of
schedule. Those outcomes describe the internal toolset as a whole, not a benchmark of this public
redirect subset.

Former colleagues may voluntarily add firsthand context in the
[colleague-perspectives thread](https://github.com/johnapaz/confluence-automation-toolkit-sample/issues/2).
Their comments represent only their personal experiences.

## Intended use

This repository exists to support a technical-writing portfolio. It is not maintained as an
operational migration resource, no production support is offered, and no license is granted.
