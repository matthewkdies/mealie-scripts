from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from mealie_scripts.commands.tags import app

runner = CliRunner()


@patch("mealie_scripts.commands.tags.MealieClient", autospec=True)
def test_list_tags(mock_mealie_client: MagicMock, capsys):
    mock_client_instance = mock_mealie_client.return_value.__aenter__.return_value
    mock_client_instance.fetch_all_tags.return_value = [
        {"id": 1, "name": "Tag 1", "slug": "tag-1"},
        {"id": 2, "name": "Tag 2", "slug": "tag-2"},
    ]

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    captured = capsys.readouterr()
    assert "ID" in captured.out
    assert "Name" in captured.out
    assert "Slug" in captured.out
    assert "Tag 1" in captured.out
    assert "tag-2" in captured.out
    mock_client_instance.fetch_all_tags.assert_awaited_once()


@patch("mealie_scripts.commands.tags.MealieClient", autospec=True)
def test_list_tags_no_tags(mock_mealie_client: MagicMock, capsys):
    mock_client_instance = mock_mealie_client.return_value.__aenter__.return_value
    mock_client_instance.fetch_all_tags.return_value = []

    result = runner.invoke(app, ["list"])

    assert result.exit_code == 0
    captured = capsys.readouterr()
    assert "ID" in captured.out
    assert "Name" in captured.out
    assert "Slug" in captured.out
    mock_client_instance.fetch_all_tags.assert_awaited_once()
