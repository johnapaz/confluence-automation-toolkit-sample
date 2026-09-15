"""Command-line interface for single-page and CSV redirect operations."""

from __future__ import annotations

import argparse
import getpass
import logging
import os
import sys
from collections.abc import Callable, Iterable
from typing import TypeVar

from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

from .client import ConfluenceClient
from .errors import ConfigurationError, ToolkitError
from .models import OperationResult, RedirectRequest
from .redirects import (
    RedirectService,
    parse_page_id_csv,
    parse_redirect_csv,
    validate_target_url,
)

console = Console()
BatchItem = TypeVar("BatchItem")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="confluence-toolkit",
        description="Add or remove versioned Confluence page redirects.",
    )
    parser.add_argument("--base-url", help="Confluence base URL; defaults to CONFLUENCE_BASE_URL.")
    parser.add_argument("--username", help="Confluence username; defaults to CONFLUENCE_USERNAME.")
    parser.add_argument("--timeout", type=float, default=30.0, help="API timeout in seconds.")
    parser.add_argument("--dry-run", action="store_true", help="Read and validate without writing.")
    parser.add_argument("--yes", action="store_true", help="Skip the final confirmation prompt.")
    parser.add_argument("--debug", action="store_true", help="Show diagnostic messages.")

    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="Add redirects to one page or a CSV batch.")
    add_source = add.add_mutually_exclusive_group(required=True)
    add_source.add_argument("--csv", help="CSV with page_id,target_url,target_title columns.")
    add_source.add_argument("--page-id", help="Confluence page ID for a single redirect.")
    add.add_argument("--target-url", help="Destination URL for --page-id.")
    add.add_argument("--target-title", help="Human-readable destination for --page-id.")

    remove = commands.add_parser("remove", help="Remove redirects from one page or a CSV batch.")
    remove_source = remove.add_mutually_exclusive_group(required=True)
    remove_source.add_argument("--csv", help="CSV with a page_id column.")
    remove_source.add_argument("--page-id", help="Confluence page ID for one removal.")
    return parser


def load_credentials(args: argparse.Namespace) -> tuple[str, str, str]:
    """Load non-secret configuration and prompt for a token when needed."""
    base_url = args.base_url or os.getenv("CONFLUENCE_BASE_URL", "")
    username = args.username or os.getenv("CONFLUENCE_USERNAME", "")
    token = os.getenv("CONFLUENCE_API_TOKEN", "")
    if not base_url:
        raise ConfigurationError("Set CONFLUENCE_BASE_URL or pass --base-url.")
    if not username:
        raise ConfigurationError("Set CONFLUENCE_USERNAME or pass --username.")
    if not token:
        token = getpass.getpass("Confluence API token: ")
    if not token:
        raise ConfigurationError("A Confluence API token is required.")
    return base_url, username, token


def collect_add_requests(args: argparse.Namespace) -> list[RedirectRequest]:
    if args.csv:
        return parse_redirect_csv(args.csv)
    if not args.target_url or not args.target_title:
        raise ConfigurationError("--page-id requires --target-url and --target-title.")
    return [
        RedirectRequest(
            args.page_id,
            validate_target_url(args.target_url),
            args.target_title.strip(),
        )
    ]


def show_plan(action: str, items: list[RedirectRequest] | list[str], dry_run: bool) -> None:
    mode = "DRY RUN" if dry_run else "WRITE"
    console.print(f"\n[bold]Plan:[/bold] {action} {len(items)} redirect(s) [{mode}]")
    table = Table("Page ID", "Target", box=None)
    for item in items[:5]:
        if isinstance(item, RedirectRequest):
            table.add_row(item.page_id, item.target_url)
        else:
            table.add_row(item, "—")
    console.print(table)
    if len(items) > 5:
        console.print(f"[dim]…and {len(items) - 5} more[/dim]")


def run_batch(
    items: Iterable[BatchItem],
    operation: Callable[[BatchItem], OperationResult],
) -> list[OperationResult]:
    results: list[OperationResult] = []
    for index, item in enumerate(items, start=1):
        result = operation(item)
        results.append(result)
        symbol = {"changed": "✓", "planned": "•", "skipped": "–", "failed": "✗"}[result.status]
        style = {"changed": "green", "planned": "cyan", "skipped": "yellow", "failed": "red"}[
            result.status
        ]
        console.print(f"[{style}]{symbol}[/] {index}: {result.page_id} — {result.message}")
        for warning in result.warnings:
            console.print(f"  [yellow]Warning:[/] {warning}")
    return results


def show_summary(results: list[OperationResult]) -> None:
    counts = {status: sum(result.status == status for result in results) for status in (
        "changed", "planned", "skipped", "failed"
    )}
    console.print(
        "\n[bold]Summary:[/bold] "
        f"changed={counts['changed']} planned={counts['planned']} "
        f"skipped={counts['skipped']} failed={counts['failed']}"
    )


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.WARNING,
        format="%(levelname)s %(message)s",
    )
    try:
        base_url, username, token = load_credentials(args)
        client = ConfluenceClient(base_url, username, token, timeout=args.timeout)
        service = RedirectService(client)

        if args.command == "add":
            items: list[RedirectRequest] | list[str] = collect_add_requests(args)
            action = "add"
        else:
            items = parse_page_id_csv(args.csv) if args.csv else [args.page_id]
            action = "remove"

        show_plan(action, items, args.dry_run)
        if not args.dry_run and not args.yes and not Confirm.ask("Continue?", default=False):
            console.print("Cancelled; no pages changed.")
            return 0

        console.print("Testing API connection…")
        client.test_connection()
        if action == "add":
            results = run_batch(
                items,
                lambda item: service.add(item, dry_run=args.dry_run),
            )
        else:
            results = run_batch(
                items,
                lambda item: service.remove(item, dry_run=args.dry_run),
            )
        show_summary(results)
        return 1 if any(result.status == "failed" for result in results) else 0
    except ToolkitError as exc:
        console.print(f"[red]Error:[/] {exc}")
        return 2
    except KeyboardInterrupt:
        console.print("\nCancelled; no further pages will be processed.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
