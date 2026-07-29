import logging
from pathlib import Path
from typing import Annotated

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from mealie_scripts.cache import CACHE_DESCRIPTIONS, CacheManager, CacheType
from mealie_scripts.config import settings

app = typer.Typer(no_args_is_help=True)
console = Console()

logger = logging.getLogger(__name__)


@app.command(name="list", help="Lists the caches available, whether they contain entries, and their descriptions.")
def list_cache(
    db_path: Annotated[Path, typer.Option(help="The path to the database file.")] = settings.sqlite_file,
) -> None:
    table = Table(title="mealie-scripts Cache")
    table.add_column("Type", style="magenta")
    table.add_column("Entries", style="cyan")
    table.add_column("Description", style="green")

    if not db_path.exists():
        for cache_type, cache_description in CACHE_DESCRIPTIONS.items():
            table.add_row(cache_type.value.title(), "0", cache_description)
    else:
        cache_manager = CacheManager(db_path)
        counts = cache_manager.get_cache_counts()
        for cache_type, cache_description in CACHE_DESCRIPTIONS.items():
            count = counts.get(cache_type, 0)
            table.add_row(cache_type.value.title(), str(count), cache_description)

    console.print(table)


@app.command(name="clear", help="Clears one or all CLI caches.")
def clear_cache(
    cache: Annotated[CacheType | None, typer.Argument(help="The cache type to clear.")] = None,
    clear_all: Annotated[bool, typer.Option("--all", "-a", help="Whether to clear all cache entries.")] = False,
    force: Annotated[bool, typer.Option("--force", "-f", help="Whether to skip the confirmation prompt.")] = False,
    db_path: Annotated[Path, typer.Option(help="The path to the database file.")] = settings.sqlite_file,
) -> None:
    if not db_path.exists():
        print("[yellow]Database file does not exist yet. Nothing to clear.[/yellow]")
        return

    cache_manager = CacheManager(db_path)

    if clear_all:
        if not force:
            typer.confirm("This will clear ALL cached recipe entries. Are you sure?", abort=True)

        cleared_count = cache_manager.clear_cache()
        print(f"[green]Successfully cleared {cleared_count} entries from all caches.[/green]")
        return

    if cache is None:
        print("[red]Error:[/red] Please specify a cache to clear (e.g., `macros`, `quick`) or use `--all`.")
        raise typer.Exit(1)

    if not force:
        typer.confirm(f"Clear the [magenta]{cache.value}[/magenta] cache?", abort=True)

    cleared_count = cache_manager.clear_cache(cache)

    if cleared_count == 0:
        print(f"No entries found for [yellow]{cache.value}[/yellow] cache.")
    else:
        print(
            f"Successfully cleared [green]{cleared_count}[/green] entries from the [magenta]{cache.value}[/magenta] cache."
        )
