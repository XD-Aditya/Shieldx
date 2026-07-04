from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table

console = Console()


def print_banner() -> None:
    try:
        from pyfiglet import Figlet

        figlet = Figlet(font="slant")
        banner = figlet.renderText("ShieldX")
        console.print(f"[bold cyan]{banner}[/bold cyan]")
        console.print("[dim]LLM validation and safety framework[/dim]\n")
    except Exception:
        console.print(
            Panel.fit(
                "[bold cyan]ShieldX[/bold cyan]\n[dim]LLM validation and safety framework[/dim]",
                border_style="cyan",
            )
        )


def print_success(message: str) -> None:
    console.print(f"[bold green]✔[/bold green] {message}")


def print_error(message: str) -> None:
    console.print(f"[bold red]✖[/bold red] {message}")


def print_warning(message: str) -> None:
    console.print(f"[bold yellow]⚠[/bold yellow] {message}")


def _preview(value, limit: int = 120) -> str:
    text = str(value).replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def render_report(report) -> None:
    status = "[bold green]PASS[/bold green]" if report.passed else "[bold red]FAIL[/bold red]"

    console.print(
        Panel.fit(
            f"Status: {status}\nRetries: [bold]{report.retries}[/bold]",
            title="ShieldX Validation Report",
            border_style="blue",
        )
    )

    console.print("[bold]Original Output:[/bold]")
    console.print(Pretty(report.original_output))
    console.print()

    console.print("[bold]Final Output:[/bold]")
    console.print(Pretty(report.final_output))
    console.print()

    table = Table(title="Validators", show_lines=True)
    table.add_column("Validator", style="cyan")
    table.add_column("Passed", justify="center")
    table.add_column("Resolved", justify="center")
    table.add_column("Code", style="magenta")
    table.add_column("Message", style="white")

    for item in report.validations:
        passed = "[green]yes[/green]" if item.passed else "[red]no[/red]"
        resolved = "[yellow]yes[/yellow]" if item.resolved else "[dim]no[/dim]"
        table.add_row(
            item.validator,
            passed,
            resolved,
            item.code or "-",
            item.message or "-",
        )

    console.print(table)

    if getattr(report, "history", None):
        history_table = Table(title="Retry History", show_lines=True)
        history_table.add_column("Attempt", justify="center", style="cyan")
        history_table.add_column("Passed", justify="center")
        history_table.add_column("Output Preview", style="white")
        history_table.add_column("Errors", style="red")

        for item in report.history:
            passed = "[green]yes[/green]" if item.passed else "[red]no[/red]"
            errors = "\n".join(item.errors) if item.errors else "-"
            history_table.add_row(
                str(item.attempt),
                passed,
                _preview(item.output),
                errors,
            )

        console.print()
        console.print(history_table)