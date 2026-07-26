import typer
from rich.console import Console

from .commands import cache, debug, recipes, tags

app = typer.Typer(
    help="A tool to manage your Mealie instance.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)

app.add_typer(cache.app, name="cache", help="Interact with the CLI's cache.")
app.add_typer(debug.app, name="debug", help="Debug the CLI.")
app.add_typer(recipes.app, name="recipes", help="Manage and analyze recipes.")
app.add_typer(tags.app, name="tags", help="Manage tags.")

console = Console()


@app.callback()
def callback():
    pass


if __name__ == "__main__":
    app()
