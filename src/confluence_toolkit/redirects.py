"""Redirect generation, CSV validation, and version-aware page operations."""

from __future__ import annotations

import csv
import logging
import re
from html import escape
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

from .errors import InputError
from .models import OperationResult, PageSnapshot, RedirectRequest

TRACKING_LABEL = "redirected"
MANAGED_MARKER = 'data-managed-by="confluence-redirect-toolkit-sample"'
MANAGED_MACRO_PATTERN = re.compile(
    rf'<ac:structured-macro\s+ac:name="html"[^>]*>'
    rf'(?:(?!</ac:structured-macro>).)*?{re.escape(MANAGED_MARKER)}'
    r"(?:(?!</ac:structured-macro>).)*?</ac:structured-macro>\s*",
    flags=re.DOTALL | re.IGNORECASE,
)
logger = logging.getLogger(__name__)


class ConfluenceGateway(Protocol):
    """Transport contract used by the redirect service and offline tests."""

    def get_page(self, page_id: str) -> PageSnapshot: ...

    def update_page(self, page: PageSnapshot, storage_value: str, version_comment: str) -> int: ...

    def add_label(self, page_id: str, label: str) -> None: ...

    def remove_label(self, page_id: str, label: str) -> None: ...


def validate_target_url(value: str) -> str:
    """Return a normalized HTTP(S) URL or raise ``InputError``."""
    candidate = value.strip()
    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise InputError(f"Invalid target URL: {value!r}")
    return candidate


def build_redirect_macro(target_url: str, target_title: str) -> str:
    """Create the Confluence storage-format HTML macro managed by this tool."""
    safe_url = escape(validate_target_url(target_url), quote=True)
    safe_title = escape(target_title.strip() or "the new location")
    return f'''<ac:structured-macro ac:name="html" ac:schema-version="1">
<ac:plain-text-body><![CDATA[<div {MANAGED_MARKER}
style="border: 2px solid #B65C00; padding: 8px; text-align: center;">
This page moved to <a href="{safe_url}">{safe_title}</a>.
<br />Use the link if you are not redirected within 5 seconds.
</div>
<meta http-equiv="refresh" content="5; URL='{safe_url}'" />]]></ac:plain-text-body>
</ac:structured-macro>'''


def remove_managed_redirect(storage_value: str) -> tuple[str, bool]:
    """Remove one redirect created by this public sample, leaving other macros intact."""
    updated, count = MANAGED_MACRO_PATTERN.subn("", storage_value, count=1)
    return updated, count == 1


def parse_redirect_csv(path: str | Path) -> list[RedirectRequest]:
    """Read and validate ``page_id,target_url,target_title`` rows."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise InputError(f"CSV file not found: {csv_path}")

    requests: list[RedirectRequest] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"page_id", "target_url", "target_title"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise InputError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        for row_number, row in enumerate(reader, start=2):
            page_id = (row.get("page_id") or "").strip()
            title = (row.get("target_title") or "").strip()
            if not page_id or not title:
                raise InputError(f"Row {row_number}: page_id and target_title are required.")
            requests.append(
                RedirectRequest(
                    page_id=page_id,
                    target_url=validate_target_url(row.get("target_url") or ""),
                    target_title=title,
                    source_row=row_number,
                )
            )

    if not requests:
        raise InputError("CSV contains headers but no redirect records.")
    return requests


def parse_page_id_csv(path: str | Path) -> list[str]:
    """Read and validate a one-column ``page_id`` removal file."""
    csv_path = Path(path)
    if not csv_path.is_file():
        raise InputError(f"CSV file not found: {csv_path}")

    page_ids: list[str] = []
    with csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if "page_id" not in (reader.fieldnames or []):
            raise InputError("CSV is missing required column: page_id")
        for row_number, row in enumerate(reader, start=2):
            page_id = (row.get("page_id") or "").strip()
            if not page_id:
                raise InputError(f"Row {row_number}: page_id is required.")
            page_ids.append(page_id)

    if not page_ids:
        raise InputError("CSV contains headers but no page IDs.")
    return page_ids


class RedirectService:
    """Coordinate reversible, versioned redirect changes through a Confluence client."""

    def __init__(self, client: ConfluenceGateway, *, label: str = TRACKING_LABEL) -> None:
        self.client = client
        self.label = label

    def add(self, request: RedirectRequest, *, dry_run: bool = False) -> OperationResult:
        """Prepend a managed redirect macro and optionally persist the new page version."""
        try:
            logger.debug("Preparing redirect addition for page %s", request.page_id)
            page = self.client.get_page(request.page_id)
            if MANAGED_MARKER in page.storage_value:
                return OperationResult(
                    page_id=page.page_id,
                    page_title=page.title,
                    action="add",
                    status="skipped",
                    message="A managed redirect is already present.",
                    previous_version=page.version,
                )

            macro = build_redirect_macro(request.target_url, request.target_title)
            updated = f"{macro}\n\n{page.storage_value}"
            if dry_run:
                return OperationResult(
                    page_id=page.page_id,
                    page_title=page.title,
                    action="add",
                    status="planned",
                    message=f"Would add redirect to {request.target_title}.",
                    previous_version=page.version,
                    new_version=page.version + 1,
                )

            new_version = self.client.update_page(
                page,
                updated,
                f"Added redirect to {request.target_title}",
            )
            warnings: list[str] = []
            try:
                self.client.add_label(page.page_id, self.label)
            except Exception as exc:
                warnings.append(f"Page updated, but tracking label was not added: {exc}")
            logger.debug(
                "Updated page %s from version %s to %s",
                page.page_id,
                page.version,
                new_version,
            )
            return OperationResult(
                page_id=page.page_id,
                page_title=page.title,
                action="add",
                status="changed",
                message=f"Added redirect to {request.target_title}.",
                previous_version=page.version,
                new_version=new_version,
                warnings=tuple(warnings),
            )
        except Exception as exc:  # Normalize row-level failures so a batch can continue.
            return OperationResult(
                page_id=request.page_id,
                page_title="Unknown page",
                action="add",
                status="failed",
                message=str(exc),
            )

    def remove(self, page_id: str, *, dry_run: bool = False) -> OperationResult:
        """Remove a managed redirect macro and optionally persist the new page version."""
        try:
            logger.debug("Preparing redirect removal for page %s", page_id)
            page = self.client.get_page(page_id)
            updated, found = remove_managed_redirect(page.storage_value)
            if not found:
                return OperationResult(
                    page_id=page.page_id,
                    page_title=page.title,
                    action="remove",
                    status="skipped",
                    message="No managed redirect was found.",
                    previous_version=page.version,
                )

            if dry_run:
                return OperationResult(
                    page_id=page.page_id,
                    page_title=page.title,
                    action="remove",
                    status="planned",
                    message="Would remove the managed redirect.",
                    previous_version=page.version,
                    new_version=page.version + 1,
                )

            new_version = self.client.update_page(page, updated, "Removed redirect macro")
            warnings: list[str] = []
            try:
                self.client.remove_label(page.page_id, self.label)
            except Exception as exc:
                warnings.append(f"Page updated, but tracking label was not removed: {exc}")
            logger.debug(
                "Updated page %s from version %s to %s",
                page.page_id,
                page.version,
                new_version,
            )
            return OperationResult(
                page_id=page.page_id,
                page_title=page.title,
                action="remove",
                status="changed",
                message="Removed the managed redirect.",
                previous_version=page.version,
                new_version=new_version,
                warnings=tuple(warnings),
            )
        except Exception as exc:  # Normalize row-level failures so a batch can continue.
            return OperationResult(
                page_id=page_id,
                page_title="Unknown page",
                action="remove",
                status="failed",
                message=str(exc),
            )
