"""Typed data exchanged between the CLI, service layer, and API client."""

from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True)
class PageSnapshot:
    """The Confluence fields required to create a new page version."""

    page_id: str
    title: str
    storage_value: str
    version: int


@dataclass(frozen=True)
class RedirectRequest:
    """One requested redirect operation."""

    page_id: str
    target_url: str
    target_title: str
    source_row: int | None = None


@dataclass(frozen=True)
class OperationResult:
    """A structured outcome suitable for console and audit-style reporting."""

    page_id: str
    page_title: str
    action: Literal["add", "remove"]
    status: Literal["changed", "skipped", "planned", "failed"]
    message: str
    previous_version: int | None = None
    new_version: int | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
