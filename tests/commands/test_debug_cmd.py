from unittest.mock import AsyncMock, MagicMock, patch

from httpx2 import ConnectError
from typer.testing import CliRunner

from mealie_scripts.commands.debug import app
from mealie_scripts.config import Settings

runner = CliRunner()


def test_show_config(mock_env: Settings):
    result = runner.invoke(app, ["show-config"])

    assert result.exit_code == 0
    assert "Name" in result.stdout
    assert "Value" in result.stdout
    assert "mealie_url" in result.stdout
    assert mock_env.mealie_url in result.stdout


@patch("mealie_scripts.commands.debug.MealieClient", autospec=True)
def test_test_connection_success(mock_mealie_client: MagicMock):
    mock_client_instance = mock_mealie_client.return_value.__aenter__.return_value
    mock_client_instance.about.return_value = AsyncMock()

    result = runner.invoke(app, ["test-connection"])

    assert result.exit_code == 0
    assert "Connection to Mealie succeeded!" in result.stdout
    mock_client_instance.about.assert_awaited_once()


@patch("mealie_scripts.commands.debug.MealieClient", autospec=True)
def test_test_connection_failure(mock_mealie_client: MagicMock):
    mock_client_instance = mock_mealie_client.return_value.__aenter__.return_value
    mock_client_instance.about.side_effect = ConnectError("Test connection error")

    result = runner.invoke(app, ["test-connection"])

    assert result.exit_code == 1
    assert "Connection to Mealie failed" in result.stdout
    mock_client_instance.about.assert_awaited_once()
