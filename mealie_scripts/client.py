import asyncio
from typing import Any

import httpx2

from .config import settings


class MealieClient:
    def __init__(self):
        self.base_url = settings.mealie_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {settings.mealie_api_token.get_secret_value()}",
            "Content-Type": "application/json",
        }
        self.client = httpx2.AsyncClient(base_url=self.base_url, headers=self.headers, timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def about(self) -> dict[str, Any]:
        """Gets information about the Mealie instance."""
        url = "/api/app/about"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def fetch_all_tags(self) -> list[dict[str, Any]]:
        """Fetches all tags from Mealie."""
        url = "/api/organizers/tags"
        params = {"page": 1, "perPage": 1000}
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])

    async def get_all_recipes(self) -> list[dict[str, Any]]:
        """Fetches all recipes using pagination."""
        recipes: list[dict[str, Any]] = []
        page = 1
        per_page = 50

        while True:
            url = "/api/recipes"
            params = {"page": page, "perPage": per_page}
            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            items = data.get("items", [])
            if not items:
                break

            recipes.extend(items)

            if len(items) < per_page:
                break

            page += 1
            await asyncio.sleep(settings.sleep_between_requests)

        return recipes

    async def get_recipe_details(self, recipe_slug: str) -> dict[str, Any] | None:
        """Fetches full recipe details."""
        url = f"/api/recipes/{recipe_slug}"
        response = await self.client.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    async def update_recipe_tags(self, recipe_slug: str, tags: list[dict[str, Any]]) -> bool:
        """Updates recipe tags via PATCH."""
        url = f"/api/recipes/{recipe_slug}"
        payload = {"tags": tags}
        response = await self.client.patch(url, json=payload)
        return response.status_code in [200, 204]

    async def create_tag(self, name: str) -> dict[str, Any]:
        """Creates a new tag."""
        url = "/api/organizers/tags"
        payload = {"name": name}
        response = await self.client.post(url, json=payload)
        response.raise_for_status()
        return response.json()
