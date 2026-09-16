"""Render sanitized Rich CLI demonstrations for the portfolio README."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.table import Table
from rich.terminal_theme import MONOKAI
from rich.text import Text

WIDTH = 96
DEMO_NOTE = "SANITIZED RECREATION  |  FICTIONAL DATA  |  NO LIVE SYSTEM"


def make_console() -> Console:
    return Console(record=True, width=WIDTH, color_system="truecolor", force_terminal=True)


def print_header(console: Console, subtitle: str) -> None:
    heading = Text("Confluence Page Redirect Manager", style="bold white")
    heading.append(f"\n{subtitle}", style="cyan")
    console.print(Panel(heading, border_style="bright_blue", padding=(1, 2)))


def print_footer(console: Console) -> None:
    console.print()
    console.print(DEMO_NOTE, justify="center", style="bold black on bright_yellow")


def render_workflow_selection(output_dir: Path) -> None:
    console = make_console()
    print_header(console, "Safe, reversible documentation operations")

    context = Table.grid(padding=(0, 2))
    context.add_column(style="bold cyan", width=18)
    context.add_column(style="white")
    context.add_row("Instance", "https://docs.example.com/confluence")
    context.add_row("Authentication", "Runtime credentials loaded; values hidden")
    context.add_row("Debug mode", "Off")
    console.print(context)
    console.print()

    menu = Table(box=box.ROUNDED, border_style="blue", show_header=False, padding=(0, 1))
    menu.add_column("Option", style="bold bright_cyan", width=8, justify="center")
    menu.add_column("Operation", style="bold white", width=38)
    menu.add_column("Input", style="dim")
    menu.add_row("1", "Add redirect to one page", "Page ID + destination")
    menu.add_row("2", "Add redirects in a batch", "CSV file")
    menu.add_row("3", "Remove redirect from one page", "Page ID")
    menu.add_row("4", "Remove redirects in a batch", "CSV file")
    console.print(menu)
    console.print()
    console.print("Select operation [1]: ", style="bold cyan", end="")
    console.print("2", style="bold green")
    console.print("Selected: Add redirects in a batch", style="green")
    print_footer(console)
    console.save_svg(
        str(output_dir / "cli-workflow-selection.svg"),
        title="Sanitized workflow selection",
        theme=MONOKAI,
    )


def render_batch_review(output_dir: Path) -> None:
    console = make_console()
    print_header(console, "Review changes before writing")

    console.print(
        Panel(
            "[bold]Plan:[/bold] add 3 redirects\n"
            "[bold]Mode:[/bold]  WRITE — confirmation required\n"
            "[bold]Source:[/bold] examples/sample-input.csv",
            title="Batch validated",
            border_style="green",
        )
    )
    preview = Table(
        "Page ID",
        "Current page",
        "Destination",
        box=box.SIMPLE_HEAVY,
        header_style="bold bright_cyan",
        row_styles=["", "dim"],
    )
    preview.add_row(
        "10001",
        "Reset a demo password",
        "kb.example.com/articles/reset-demo-password",
    )
    preview.add_row(
        "10002",
        "Request demo access",
        "kb.example.com/articles/request-demo-access",
    )
    preview.add_row(
        "10003",
        "Update a demo profile",
        "kb.example.com/articles/update-demo-profile",
    )
    console.print(preview)
    console.print("Validation: ", style="bold", end="")
    console.print("3 records ready; 0 rejected", style="bold green")
    console.print("Versioning: ", style="bold", end="")
    console.print("minor edit + human-readable version comment", style="white")
    console.print()
    prompt = Text("Continue with 3 page updates? [y/N]: ", style="bold yellow")
    console.print(prompt, end="")
    console.print("y", style="bold green")
    print_footer(console)
    console.save_svg(
        str(output_dir / "cli-batch-review.svg"),
        title="Sanitized batch review",
        theme=MONOKAI,
    )


def render_processing_results(output_dir: Path) -> None:
    console = make_console()
    print_header(console, "Visible progress and per-page outcomes")

    console.print("Processing redirects", style="bold bright_cyan")
    console.print(ProgressBar(total=3, completed=3, width=66, pulse=False))
    console.print()

    results = Table(box=box.ROUNDED, border_style="blue", padding=(0, 1))
    results.add_column("Result", width=10)
    results.add_column("Page", width=35)
    results.add_column("Audit detail")
    results.add_row(
        "[bold green]CHANGED[/]",
        "10001  Reset a demo password",
        "version 7 -> 8; label added",
    )
    results.add_row(
        "[bold green]CHANGED[/]",
        "10002  Request demo access",
        "version 11 -> 12; label added",
    )
    results.add_row(
        "[bold red]FAILED[/]",
        "10003  Update a demo profile",
        "HTTP 403; page unchanged",
    )
    console.print(results)
    console.print()
    summary = Table.grid(padding=(0, 2))
    summary.add_column(style="bold", width=16)
    summary.add_column()
    summary.add_row("Changed", "[green]2[/]")
    summary.add_row("Skipped", "[yellow]0[/]")
    summary.add_row("Failed", "[red]1[/]")
    summary.add_row(
        "Next step",
        "Review the failed page; successful pages remain traceable in history",
    )
    console.print(Panel(summary, title="Batch complete", border_style="bright_blue"))
    print_footer(console)
    console.save_svg(
        str(output_dir / "cli-processing-results.svg"),
        title="Sanitized processing results",
        theme=MONOKAI,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("assets"),
        help="Directory for generated SVG files (default: assets)",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    render_workflow_selection(args.output_dir)
    render_batch_review(args.output_dir)
    render_processing_results(args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
