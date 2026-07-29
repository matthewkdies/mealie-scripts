from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx2
import pytest
from pydantic import SecretStr

from mealie_scripts.cache import CacheManager
from mealie_scripts.client import MealieClient
from mealie_scripts.config import Settings


@pytest.fixture
def mock_settings(tmp_path: Path) -> Settings:
    return Settings(
        mealie_url="http://test-mealie.dne",
        mealie_api_token=SecretStr("test-token"),
        sleep_between_requests=0,
        sqlite_file=tmp_path / "test.db",
    )


@pytest.fixture
def mock_httpx_client() -> MagicMock:
    return MagicMock(spec=httpx2.AsyncClient)


@pytest.fixture
def mealie_client(mock_settings: Settings, mock_httpx_client: MagicMock) -> MealieClient:
    with patch("mealie_scripts.client.httpx2.AsyncClient", return_value=mock_httpx_client):
        client = MealieClient(mock_settings, mock_httpx_client)
        return client


@pytest.fixture
def cache_manager(mock_settings: Settings) -> CacheManager:
    """Returns a CacheManager instance with a temporary db path."""
    return CacheManager(mock_settings.sqlite_file)


# TODO: can't figure out how to get env vars up at runtime for the CLI invocation
@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch, mock_settings: Settings):
    """Mock environment variables for settings."""
    for setting_name, setting_val in mock_settings:
        monkeypatch.setenv(f"MEALIE_SCRIPTS_{setting_name.upper()}", str(setting_val))
    return mock_settings
