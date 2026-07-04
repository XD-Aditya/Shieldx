from __future__ import annotations

from shieldx.version import __version__
from shieldx.cli.ui import console, print_banner


def version_command() -> None:
    print_banner()
    console.print(f"[bold]Version:[/bold] [cyan]{__version__}[/cyan]")