import asyncio

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from ..client import MealieClient
from ..config import settings
from ..utils import load_cache, save_cache

app = typer.Typer(no_args_is_help=True)
console = Console()


async def get_or_create_tag(client: MealieClient, tag_name: str, system_tags: dict):
    if tag_name in system_tags:
        return system_tags[tag_name]

    console.print(f"[yellow]Tag '{tag_name}' not found. Creating it...[/yellow]")
    return await client.create_tag(tag_name)


@app.command(name="check-macros")
def check_macros(force: bool = typer.Option(False, "--force", "-f", help="Ignore cache and check all recipes.")):
    """
    Check all recipes for protein and fiber thresholds and apply tags.
    """

    async def _run():
        processed_cache = load_cache("macros") if not force else set()

        async with MealieClient() as client:
            console.print("[bold blue]Fetching system tags...[/bold blue]")
            tags_list = await client.fetch_all_tags()
            system_tags = {t["name"]: t for t in tags_list}

            protein_tag = await get_or_create_tag(client, settings.protein_tag_name, system_tags)
            fiber_tag = await get_or_create_tag(client, settings.fiber_tag_name, system_tags)

            console.print("[bold blue]Fetching all recipes...[/bold blue]")
            all_recipes = await client.get_all_recipes()

            recipes_to_process = [r for r in all_recipes if r["id"] not in processed_cache]

            if not recipes_to_process:
                console.print("[green]No new recipes to process.[/green]")
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Processing recipes...", total=len(recipes_to_process))

                for summary in recipes_to_process:
                    recipe_slug = summary.get("slug")
                    recipe_name = summary.get("name")
                    progress.update(task, description=f"Processing '{recipe_name}'")

                    recipe = await client.get_recipe_details(recipe_slug)
                    if not recipe:
                        progress.advance(task)
                        continue

                    nutrition = recipe.get("nutrition", {}) or {}
                    try:
                        protein = float(nutrition.get("proteinContent") or 0)
                        fiber = float(nutrition.get("fiberContent") or 0)
                    except (ValueError, TypeError):
                        protein = 0.0
                        fiber = 0.0

                    existing_tags = recipe.get("tags", []) or []
                    existing_tag_names = {t["name"] if isinstance(t, dict) else str(t) for t in existing_tags}

                    tag_payloads = [t if isinstance(t, dict) else {"name": str(t)} for t in existing_tags]
                    needs_update = False

                    if protein >= settings.protein_threshold and settings.protein_tag_name not in existing_tag_names:
                        tag_payloads.append(protein_tag)
                        existing_tag_names.add(settings.protein_tag_name)
                        needs_update = True

                    if fiber >= settings.fiber_threshold and settings.fiber_tag_name not in existing_tag_names:
                        tag_payloads.append(fiber_tag)
                        existing_tag_names.add(settings.fiber_tag_name)
                        needs_update = True

                    if needs_update:
                        await client.update_recipe_tags(recipe_slug, tag_payloads)

                    processed_cache.add(summary["id"])
                    save_cache("macros", processed_cache)
                    progress.advance(task)
                    await asyncio.sleep(settings.sleep_between_requests)

    asyncio.run(_run())


# TODO: doesn't _seem_ to be working
# I can't figure out an easy way to remove all of the "quick" tags from recipes to be certain though
@app.command(name="check-quick")
def check_quick(force: bool = typer.Option(False, "--force", "-f", help="Ignore cache and check all recipes.")):
    """
    Check all recipes for totalTime threshold and apply the quick tag.
    """

    async def _run():
        processed_cache = load_cache("quick") if not force else set()

        async with MealieClient() as client:
            console.print("[bold blue]Fetching system tags...[/bold blue]")
            tags_list = await client.fetch_all_tags()
            system_tags = {t["name"]: t for t in tags_list}

            quick_tag = await get_or_create_tag(client, settings.quick_tag_name, system_tags)

            console.print("[bold blue]Fetching all recipes...[/bold blue]")
            all_recipes = await client.get_all_recipes()

            recipes_to_process = [r for r in all_recipes if r["id"] not in processed_cache]

            if not recipes_to_process:
                console.print("[green]No new recipes to process.[/green]")
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task("Processing quick recipes...", total=len(recipes_to_process))

                for summary in recipes_to_process:
                    recipe_slug = summary.get("slug")
                    recipe_name = summary.get("name")
                    progress.update(task, description=f"Checking '{recipe_name}'")

                    recipe = await client.get_recipe_details(recipe_slug)
                    if not recipe:
                        progress.advance(task)
                        continue

                    # Mealie totalTime is often in ISO 8601 format (e.g. PT30M) or a string.
                    # We need a robust parser. For now let's assume it's something we can handle.
                    # Actually, Mealie's totalTime in the API is often null or a string.
                    total_time_str = recipe.get("totalTime", "") or ""

                    # Very basic ISO 8601 duration parser for minutes
                    import re

                    minutes = 0
                    if total_time_str:
                        match = re.search(r"PT(?:(\d+)H)?(?:(\d+)M)?", total_time_str)
                        if match:
                            hours = int(match.group(1) or 0)
                            mins = int(match.group(2) or 0)
                            minutes = hours * 60 + mins

                    existing_tags = recipe.get("tags", []) or []
                    existing_tag_names = {t["name"] if isinstance(t, dict) else str(t) for t in existing_tags}

                    if (
                        0 < minutes <= settings.quick_threshold_minutes
                        and settings.quick_tag_name not in existing_tag_names
                    ):
                        tag_payloads = [t if isinstance(t, dict) else {"name": str(t)} for t in existing_tags]
                        tag_payloads.append(quick_tag)
                        await client.update_recipe_tags(recipe_slug, tag_payloads)

                    processed_cache.add(summary["id"])
                    save_cache("quick", processed_cache)
                    progress.advance(task)
                    await asyncio.sleep(settings.sleep_between_requests)

    asyncio.run(_run())
