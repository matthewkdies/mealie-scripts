import logging
from typing import Annotated

import typer
from rich import print
from rich.console import Console
from rich.table import Table

from mealie_scripts.cache import CACHE_DESCRIPTIONS
from mealie_scripts.config import settings

app = typer.Typer(no_args_is_help=True)
console = Console()

logger = logging.getLogger(__name__)


@app.command(name="list", help="Lists the caches available, whether they exist, and their descriptions.")
def list_cache() -> None:
    table = Table(title="mealie-scripts Cache")
    table.add_column("Type", style="magenta")
    table.add_column("Exists")
    table.add_column("Description", style="green")

    for cache_type, cache_description in CACHE_DESCRIPTIONS.items():
        cache_name = cache_type.value
        exists = settings.get_cache_file(cache_name).is_file()
        exists_str = "✅" if exists else "❌"
        table.add_row(cache_name.title(), exists_str, cache_description)

    console.print(table)


@app.command(name="clear", help="Clears one or all CLI caches.")
def clear_cache(
    cache: Annotated[str | None, typer.Argument(help="The cache to clear.")] = None,
    clear_all: Annotated[bool, typer.Option("--all", "-a", help="Whether to clear all cache files.")] = False,
    force: Annotated[bool, typer.Option("--force", "-f", help="Whether to skip the confirmation prompt.")] = False,
) -> None:
    if clear_all:
        if not force:
            typer.confirm("This will clear all cache. Are you sure?", abort=True)
        cache_contents = settings.config_dir.glob("*.json")
        for cache_file in cache_contents:
            cache_file.unlink()
    if not cache:
        print("No cache provided. Provide a cache argument to clear a single cache.")
        raise typer.Exit(1)
    cache_file = settings.config_dir / f"{cache}.json"
    if not cache_file.is_file():
        raise FileNotFoundError(cache_file)
    cache_file.unlink()
    print(f"Successfully cleared the [green]{cache}[/green] cache.")
