from unittest.mock import MagicMock, patch

import httpx2
import pytest
from pydantic import SecretStr

from mealie_scripts.client import MealieClient
from mealie_scripts.config import Settings


@pytest.fixture
def mock_settings() -> Settings:
    return Settings(
        mealie_url="http://test-mealie.dne",
        mealie_api_token=SecretStr("test-token"),
        sleep_between_requests=0,
    )


@pytest.fixture
def mock_httpx_client() -> MagicMock:
    return MagicMock(spec=httpx2.AsyncClient)


@pytest.fixture
def mealie_client(mock_settings: Settings, mock_httpx_client: MagicMock) -> MealieClient:
    with patch("mealie_scripts.client.httpx2.AsyncClient", return_value=mock_httpx_client):
        client = MealieClient(mock_settings, mock_httpx_client)
        return client
