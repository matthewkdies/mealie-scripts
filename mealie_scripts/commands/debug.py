import asyncio
import logging

import typer
from httpx2 import ConnectError
from rich import print
from rich.console import Console
from rich.table import Table

from mealie_scripts.client import MealieClient
from mealie_scripts.config import settings

app = typer.Typer(no_args_is_help=True)
console = Console()

logger = logging.getLogger(__name__)


@app.command(name="show-config", help="Shows the CLI's configuration from the settings.")
def show_config():
    table = Table(title="mealie-scripts Config")
    table.add_column("Name", style="magenta")
    table.add_column("Value", style="green")

    for setting in settings:
        table.add_row(setting[0], str(setting[1]))

    console.print(table)


@app.command(name="test-connection", help="Tests the connection to the Mealie instance from the CLI's settings.")
def test_connection():
    async def _test_connection():
        async with MealieClient() as client:
            return await client.about()

    try:
        asyncio.run(_test_connection())
        print("Connection to Mealie succeeded!")
    except ConnectError:  # TODO: definitely more exceptions needed here
        print("Connection to Mealie failed. Confirm settings with [green]mealie-scripts debug show-config[/green].")
        raise typer.Exit(1)
