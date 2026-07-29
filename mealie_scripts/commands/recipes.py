import asyncio
import re
from collections.abc import Callable
from typing import Any

import typer
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn

from mealie_scripts.cache import CacheManager, CacheType
from mealie_scripts.client import MealieClient
from mealie_scripts.config import settings

app = typer.Typer(no_args_is_help=True)
console = Console()

# Pre-compile patterns for efficiency
HOURS_REGEX = re.compile(r"(\d+)\s*(?:hours?|hrs?|h)\b", re.IGNORECASE)
MINUTES_REGEX = re.compile(r"(\d+)\s*(?:minutes?|mins?|m)\b", re.IGNORECASE)

# --- Helper Functions ---


async def get_or_create_tag(client: MealieClient, tag_name: str, system_tags: dict[str, Any]) -> dict[str, Any]:
    if tag_name in system_tags:
        return system_tags[tag_name]

    console.print(f"[yellow]Tag '{tag_name}' not found. Creating it...[/yellow]")
    return await client.create_tag(tag_name)


def parse_total_time_for_minutes(duration_str: str | None) -> int:
    """Extract total minutes from an ISO 8601 duration string."""
    if not duration_str or not isinstance(duration_str, str):
        return 0

    duration_str = duration_str.strip().lower()
    total_minutes = 0
    hours_match = HOURS_REGEX.search(duration_str)
    if hours_match:
        total_minutes += int(hours_match.group(1)) * 60
    mins_match = MINUTES_REGEX.search(duration_str)
    if mins_match:
        total_minutes += int(mins_match.group(1))

    # edge case: If no unit labels were found but it's just a raw number (e.g., "30"), treat as minutes
    if total_minutes == 0 and duration_str.isdigit():
        total_minutes = int(duration_str)

    return total_minutes


def extract_tag_payloads(recipe: dict[str, Any]) -> tuple[list[dict[str, Any]], set[str]]:
    """Normalize existing tags into a payload list and a set of tag names."""
    existing_tags = recipe.get("tags", []) or []
    tag_names = {t["name"] for t in existing_tags}
    payloads = [t for t in existing_tags]
    return payloads, tag_names


async def run_recipe_processor(
    cache_type: CacheType,
    force: bool,
    process_single_recipe: Callable[[MealieClient, dict[str, Any], dict[str, Any]], Any],
):
    """Generic runner that handles client connection, cache, and progress bar UI."""
    cache_manager = CacheManager(settings.sqlite_file)
    processed_cache = cache_manager.load_cache(cache_type.name) if not force else set()

    async with MealieClient() as client:
        console.print("[bold blue]Fetching system tags...[/bold blue]")
        tags_list = await client.fetch_all_tags()
        system_tags = {t["name"]: t for t in tags_list}

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
                if recipe:
                    await process_single_recipe(client, recipe, system_tags)

                processed_cache.add(summary["id"])
                cache_manager.add_to_cache(cache_type, processed_cache)
                progress.advance(task)
                await asyncio.sleep(settings.sleep_between_requests)


# --- Core Recipe Processors ---


async def process_macros_for_recipe(client: MealieClient, recipe: dict[str, Any], system_tags: dict[str, Any]):
    protein_tag = await get_or_create_tag(client, settings.protein_tag_name, system_tags)
    fiber_tag = await get_or_create_tag(client, settings.fiber_tag_name, system_tags)

    nutrition = recipe.get("nutrition") or {}
    try:
        protein = float(nutrition.get("proteinContent") or 0)
        fiber = float(nutrition.get("fiberContent") or 0)
    except (ValueError, TypeError):
        protein = 0.0
        fiber = 0.0

    tag_payloads, existing_tag_names = extract_tag_payloads(recipe)
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
        await client.update_recipe_tags(recipe["slug"], tag_payloads)


async def process_quick_for_recipe(client: MealieClient, recipe: dict[str, Any], system_tags: dict[str, Any]):
    quick_tag = await get_or_create_tag(client, settings.quick_tag_name, system_tags)
    minutes = parse_total_time_for_minutes(recipe.get("totalTime"))

    tag_payloads, existing_tag_names = extract_tag_payloads(recipe)

    if 0 < minutes <= settings.quick_threshold_minutes and settings.quick_tag_name not in existing_tag_names:
        tag_payloads.append(quick_tag)
        await client.update_recipe_tags(recipe["slug"], tag_payloads)


# --- Typer CLI Commands ---


@app.command(name="check-macros")
def check_macros(force: bool = typer.Option(False, "--force", "-f", help="Ignore cache and check all recipes.")):
    """Check all recipes for protein and fiber thresholds and apply tags."""
    asyncio.run(run_recipe_processor(CacheType.MACROS, force, process_macros_for_recipe))


@app.command(name="check-quick")
def check_quick(force: bool = typer.Option(False, "--force", "-f", help="Ignore cache and check all recipes.")):
    """Check all recipes for totalTime threshold and apply the quick tag."""
    asyncio.run(run_recipe_processor(CacheType.QUICK, force, process_quick_for_recipe))
