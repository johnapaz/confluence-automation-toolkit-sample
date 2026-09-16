# Contribution statement

This document distinguishes the original internal tool family from the public reconstruction in
this repository.

## Original internal tools — John Paz

John's contribution included:

- recognizing that the migration's repetitive Confluence work was a suitable automation problem;
- defining requirements, edge cases, operator workflows, and success criteria;
- designing confirmations, debug output, progress feedback, version comments, and recovery paths;
- directing AI-assisted implementation and reviewing generated changes;
- testing changes against real migration scenarios and correcting failures;
- maintaining functioning versions in Git as the utilities evolved;
- documenting installation and use so colleagues could reproduce the workflows; and
- supporting the six teammates who came to rely on the tools.

The original tools ran in the working environment and contributed to the reported operational
results.

## Public reconstruction — John Paz and OpenAI Codex

John supplied the original archives and project history, selected the representative workflow,
defined the intended audience, established confidentiality constraints, reviewed the proposed
positioning, and approved the reconstruction strategy.

OpenAI Codex inspected the archives and performed much of the public code's sanitization,
restructuring, test creation, documentation, packaging, and presentation under John's direction.
The screenshots were generated from Rich terminal components with fictional data.

John has not manually written or independently validated every line in the current repository. The
public reconstruction has offline unit-test coverage but has not been integration-tested against a
live Confluence API.

## What this artifact supports

This case study supports claims about John's:

- problem framing and requirements development;
- documentation-operations experience;
- familiarity with REST APIs, CLI workflows, and batch processing;
- attention to usability, safeguards, auditability, and reproducibility;
- ability to evaluate and maintain AI-assisted technical work; and
- measurable impact with the original internal tool family.

It does not claim that John hand-authored every line of this reconstruction, that this public
package was deployed at Airbnb, that it is production-ready, or that Airbnb endorses it.

## Employer relationship

John developed the original tools while working as a contract technical writer supporting Airbnb.
This repository contains no employer source files, production credentials, internal URLs, or
production data. Airbnb did not sponsor, review, or endorse the reconstruction.
