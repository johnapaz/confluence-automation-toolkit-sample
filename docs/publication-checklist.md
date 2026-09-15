# Publication checklist

Complete this owner review before merging the portfolio branch or sharing the repository in an
application.

## Confidentiality

- [ ] Search the full branch and Git history for internal domains, internal source-control hosts,
  team names, employee names, project keys, real page/solution IDs, and copied production content.
- [ ] Confirm that every Airbnb reference is an intentional high-level attribution and reveals no
  internal implementation detail.
- [ ] Confirm that no original ZIP, archive listing, extracted directory, `.env`, credential store,
  terminal transcript, screenshot, or generated report is tracked.
- [ ] Run a secret scanner available in your own development environment and investigate every
  finding, including findings in Git history.
- [ ] Confirm that every domain and identifier in examples is intentionally fictional.

## Accuracy

- [ ] Confirm the description of John's contract relationship with Airbnb is accurate and permitted
  by any applicable agreement.
- [ ] Read `README.md` and `PORTFOLIO-NOTE.md` in your own voice; revise any claim you would not be
  comfortable explaining in an interview.
- [ ] Confirm the statements “used by six colleagues,” “saved hundreds of hours,” and “helped finish
  ahead of schedule” are accurate and supportable.
- [ ] Confirm that the impact statements clearly refer to the original tool family, not this sample
  alone.
- [ ] Verify that the description of your AI-assisted workflow matches how you actually worked.
- [ ] Confirm the public reconstruction is described as offline-tested but not live
  integration-tested.
- [ ] Confirm that naming Airbnb is permitted; keep the migration destination and internal systems
  generalized unless separately authorized.

## Technical review

- [ ] Run `pytest` and `ruff check .` from a clean virtual environment.
- [ ] Test only against a non-production Confluence space you are authorized to modify.
- [ ] Confirm the target deployment's authentication scheme, API paths, HTML macro policy, and
  support for `minorEdit` and version messages.
- [ ] Exercise add, repeated add, dry run, remove, missing redirect, invalid row, denied page, and
  label-failure scenarios.
- [ ] Review dependency versions and any automated security alerts before release.

## Repository presentation

- [ ] Confirm every CLI image is labeled as a sanitized recreation using fictional data.
- [ ] Obtain explicit permission before quoting or identifying a former colleague outside their own
  public comment.
- [ ] Review the draft pull request file by file and confirm only reconstructed portfolio files are
  present.
- [ ] Check Markdown links, Mermaid rendering, code blocks, and the CLI help output on GitHub.
- [ ] Decide whether to add a license after confirming ownership and distribution rights. Do not
  assume public visibility grants reuse rights.
- [ ] Add repository topics and a concise description only after the content review is complete.
- [ ] Merge only after the checklist is complete; delete the build branch afterward if desired.
