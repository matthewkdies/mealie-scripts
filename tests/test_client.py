from unittest.mock import MagicMock, patch

import pytest

from mealie_scripts.client import MealieClient
from mealie_scripts.config import Settings


def test_mealie_client_init(mock_settings: Settings):
    with patch("mealie_scripts.client.httpx2.AsyncClient") as mock_client_constructor:
        client = MealieClient(mock_settings)
        mock_client_constructor.assert_called_once_with(
            base_url=mock_settings.mealie_url,
            headers={
                "Authorization": f"Bearer {mock_settings.mealie_api_token.get_secret_value()}",
                "Content-Type": "application/json",
            },
            timeout=30,
        )
        assert client.settings == mock_settings


@pytest.mark.asyncio
async def test_about(mealie_client: MealieClient, mock_httpx_client: MagicMock):
    mock_response = MagicMock()
    mock_response.json.return_value = {"version": "9.9.9"}
    mock_httpx_client.get.return_value = mock_response

    result = await mealie_client.about()

    assert result
    mock_httpx_client.get.assert_called_once_with("/api/app/about")


@pytest.mark.asyncio
async def test_get_all_tags(mealie_client: MealieClient, mock_httpx_client: MagicMock):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {  # stolen STRAIGHT from mealie API docs
        "page": 1,
        "per_page": 1000,
        "total": 1,
        "total_pages": 1,
        "items": [{"id": "tag_id", "groupId": "group_id", "name": "tag_name", "slug": "tag_slug"}],
        "next": "string",
        "previous": "string",
    }
    mock_httpx_client.get.return_value = mock_response

    tags = await mealie_client.fetch_all_tags()

    assert len(tags) == 1
    assert tags[0]["name"] == "tag_name"
    mock_httpx_client.get.assert_called_once_with("/api/organizers/tags", params={"page": 1, "per_page": 1000})


@pytest.mark.asyncio
async def test_get_all_recipes(mealie_client: MealieClient, mock_httpx_client: MagicMock):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {  # stolen STRAIGHT from mealie API docs
        "page": 1,
        "per_page": 10,
        "total": 0,
        "total_pages": 0,
        "items": [
            {
                "id": "string",
                "userId": "string",
                "householdId": "string",
                "groupId": "string",
                "name": "recipe_name",
                "slug": "",
                "image": "string",
                "recipeServings": 0,
                "recipeYieldQuantity": 0,
                "recipeYield": "string",
                "totalTime": "string",
                "prepTime": "string",
                "cookTime": "string",
                "performTime": "string",
                "description": "",
                "recipeCategory": [],
                "tags": [],
                "tools": [],
                "rating": 0,
                "orgURL": "string",
                "dateAdded": "2026-07-28",
                "dateUpdated": "2026-07-28T02:31:48.454Z",
                "createdAt": "2026-07-28T02:31:48.454Z",
                "updatedAt": "2026-07-28T02:31:48.454Z",
                "lastMade": "2026-07-28T02:31:48.454Z",
            }
        ],
        "next": "string",
        "previous": "string",
    }
    mock_httpx_client.get.return_value = mock_response

    recipes = await mealie_client.get_all_recipes()

    assert len(recipes) == 1
    assert recipes[0]["name"] == "recipe_name"

    # Check that get was called with the correct params
    mock_httpx_client.get.assert_called_once_with("/api/recipes", params={"page": 1, "per_page": 50})


# def test_update_recipe(mealie_client: MealieClient, mock_httpx_client: MagicMock):
#     recipe_id = "recipe-slug"
#     updated_recipe_data = {"name": "Updated Recipe Name"}

#     mock_response = MagicMock()
#     mock_response.raise_for_status.return_value = None
#     mock_response.json.return_value = {"id": recipe_id, **updated_recipe_data}
#     mock_httpx_client.put.return_value = mock_response

#     response_data = mealie_client.update_recipe(recipe_id, updated_recipe_data)

#     assert response_data["name"] == "Updated Recipe Name"
#     mock_httpx_client.put.assert_called_once_with(f"/api/recipes/{recipe_id}", json=updated_recipe_data)
