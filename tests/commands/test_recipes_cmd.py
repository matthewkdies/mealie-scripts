from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from mealie_scripts.cache import CacheType
from mealie_scripts.commands.recipes import (
    app,
    extract_tag_payloads,
    get_or_create_tag,
    parse_total_time_for_minutes,
    process_macros_for_recipe,
    process_quick_for_recipe,
)
from mealie_scripts.config import Settings

runner = CliRunner()


@pytest.mark.parametrize(
    ("duration_str", "expected_minutes"),
    [
        ("1 hour 30 minutes", 90),
        ("45 minutes", 45),
        ("2h", 120),
        ("15m", 15),
        ("30", 30),
        ("1 hour", 60),
        ("1hr", 60),
        (None, 0),
        ("", 0),
        ("just text", 0),
    ],
)
def test_parse_total_time_for_minutes(duration_str, expected_minutes):
    assert parse_total_time_for_minutes(duration_str) == expected_minutes


def test_extract_tag_payloads():
    recipe = {"tags": [{"name": "tag1"}, {"name": "tag2"}]}
    payloads, tag_names = extract_tag_payloads(recipe)
    assert tag_names == {"tag1", "tag2"}
    assert payloads == [{"name": "tag1"}, {"name": "tag2"}]


def test_extract_tag_payloads_no_tags():
    recipe = {}
    payloads, tag_names = extract_tag_payloads(recipe)
    assert tag_names == set()
    assert payloads == []


@pytest.mark.asyncio
async def test_get_or_create_tag_exists():
    client = MagicMock()
    system_tags = {"existing-tag": {"name": "existing-tag", "id": 1}}
    tag = await get_or_create_tag(client, "existing-tag", system_tags)
    assert tag["name"] == "existing-tag"
    client.create_tag.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_tag_creates():
    client = AsyncMock()
    client.create_tag.return_value = {"name": "new-tag", "id": 2}
    system_tags = {"existing-tag": {"name": "existing-tag", "id": 1}}
    tag = await get_or_create_tag(client, "new-tag", system_tags)
    assert tag["name"] == "new-tag"
    client.create_tag.assert_awaited_once_with("new-tag")


@pytest.mark.asyncio
async def test_process_macros_for_recipe_protein(mock_settings: Settings, mealie_client: MagicMock):
    recipe = {"slug": "test-recipe", "nutrition": {"proteinContent": 35}}
    mock_settings.protein_threshold = 30
    system_tags = {}
    mealie_client.create_tag.return_value = {"name": mock_settings.protein_tag_name}

    await process_macros_for_recipe(mealie_client, recipe, system_tags)

    mealie_client.update_recipe_tags.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_macros_for_recipe_fiber(mock_settings: Settings, mealie_client: MagicMock):
    recipe = {"slug": "test-recipe", "nutrition": {"fiberContent": 15}}
    mock_settings.fiber_threshold = 10
    system_tags = {}
    mealie_client.create_tag.return_value = {"name": mock_settings.fiber_tag_name}

    await process_macros_for_recipe(mealie_client, recipe, system_tags)

    mealie_client.update_recipe_tags.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_macros_for_recipe_no_update(mock_settings: Settings, mealie_client: MagicMock):
    recipe = {"slug": "test-recipe", "nutrition": {"proteinContent": 10, "fiberContent": 5}}
    mock_settings.protein_threshold = 30
    mock_settings.fiber_threshold = 10
    system_tags = {}

    await process_macros_for_recipe(mealie_client, recipe, system_tags)

    mealie_client.update_recipe_tags.assert_not_called()


@pytest.mark.asyncio
async def test_process_quick_for_recipe(mock_settings: Settings, mealie_client: MagicMock):
    recipe = {"slug": "test-recipe", "totalTime": "20 minutes"}
    mock_settings.quick_threshold_minutes = 30
    system_tags = {}
    mealie_client.create_tag.return_value = {"name": mock_settings.quick_tag_name}

    await process_quick_for_recipe(mealie_client, recipe, system_tags)

    mealie_client.update_recipe_tags.assert_awaited_once()


@pytest.mark.asyncio
async def test_process_quick_for_recipe_no_update(mock_settings: Settings, mealie_client: MagicMock):
    recipe = {"slug": "test-recipe", "totalTime": "45 minutes"}
    mock_settings.quick_threshold_minutes = 30
    system_tags = {}

    await process_quick_for_recipe(mealie_client, recipe, system_tags)

    mealie_client.update_recipe_tags.assert_not_called()


@patch("mealie_scripts.commands.recipes.run_recipe_processor")
def test_check_macros_command(mock_run_recipe_processor):
    result = runner.invoke(app, ["check-macros"])
    assert result.exit_code == 0
    mock_run_recipe_processor.assert_called_once_with(CacheType.MACROS, False, process_macros_for_recipe)


@patch("mealie_scripts.commands.recipes.run_recipe_processor")
def test_check_macros_command_force(mock_run_recipe_processor):
    result = runner.invoke(app, ["check-macros", "--force"])
    assert result.exit_code == 0
    mock_run_recipe_processor.assert_called_once_with(CacheType.MACROS, True, process_macros_for_recipe)


@patch("mealie_scripts.commands.recipes.run_recipe_processor")
def test_check_quick_command(mock_run_recipe_processor):
    result = runner.invoke(app, ["check-quick"])
    assert result.exit_code == 0
    mock_run_recipe_processor.assert_called_once_with(CacheType.QUICK, False, process_quick_for_recipe)


@patch("mealie_scripts.commands.recipes.run_recipe_processor")
def test_check_quick_command_force(mock_run_recipe_processor):
    result = runner.invoke(app, ["check-quick", "--force"])
    assert result.exit_code == 0
    mock_run_recipe_processor.assert_called_once_with(CacheType.QUICK, True, process_quick_for_recipe)
