import asyncio

import typer
from rich.console import Console
from rich.table import Table

from ..client import MealieClient

app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command(name="list")
def list_tags():
    """
    List all tags in Mealie.
    """

    async def _list():
        async with MealieClient() as client:
            tags = await client.fetch_all_tags()

            table = Table(title="Mealie Tags")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Slug", style="green")

            for tag in tags:
                table.add_row(str(tag.get("id")), tag.get("name"), tag.get("slug"))

            console.print(table)

    asyncio.run(_list())
