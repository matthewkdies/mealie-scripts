from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from mealie_scripts.cache import CacheManager, CacheType
from mealie_scripts.commands.cache import app

runner = CliRunner()


@pytest.fixture
def mock_cache_manager(tmp_path: Path) -> MagicMock:
    return MagicMock(spec=CacheManager)


def test_list_cache_no_db(mock_settings, capsys):
    db_path = mock_settings.sqlite_file
    result = runner.invoke(app, ["list", "--db-path", str(db_path)])

    assert result.exit_code == 0
    captured = capsys.readouterr()
    assert "Type" in captured.out
    assert "Entries" in captured.out
    assert "Description" in captured.out
    assert "Macros" in captured.out
    assert "0" in captured.out


def test_list_cache_with_db(cache_manager: CacheManager, mock_settings):
    db_path = mock_settings.sqlite_file
    cache_manager.update_cache(CacheType.QUICK, {"test": "data"})
    result = runner.invoke(app, ["list", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "Quick" in result.stdout
    assert "1" in result.stdout


def test_clear_cache_no_db(mock_settings, capsys):
    db_path = mock_settings.sqlite_file
    result = runner.invoke(app, ["clear", "--db-path", str(db_path)])

    assert result.exit_code == 0
    captured = capsys.readouterr()
    assert "Database file does not exist yet" in captured.out


def test_clear_cache_all(cache_manager: CacheManager, mock_settings):
    db_path = mock_settings.sqlite_file
    cache_manager.update_cache(CacheType.QUICK, {"test": "data"})
    cache_manager.update_cache(CacheType.MACROS, {"test": "data"})

    result = runner.invoke(app, ["clear", "--all", "--force", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "Successfully cleared 2 entries from all caches" in result.stdout
    assert cache_manager.get_cache_counts() == {}


def test_clear_cache_all_confirm(cache_manager: CacheManager, mock_settings):
    db_path = mock_settings.sqlite_file
    cache_manager.update_cache(CacheType.QUICK, {"test": "data"})
    result = runner.invoke(app, ["clear", "--all", "--db-path", str(db_path)], input="y\n")

    assert result.exit_code == 0
    assert "Successfully cleared 1 entries from all caches" in result.stdout


def test_clear_cache_specific(cache_manager: CacheManager, mock_settings):
    db_path = mock_settings.sqlite_file
    cache_manager.update_cache(CacheType.QUICK, {"test": "data"})
    cache_manager.update_cache(CacheType.MACROS, {"test": "data"})

    result = runner.invoke(app, ["clear", "quick", "--force", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "Successfully cleared 1 entries from the Quick cache" in result.stdout
    assert cache_manager.get_cache_counts()[CacheType.MACROS] == 1
    assert CacheType.QUICK not in cache_manager.get_cache_counts()


def test_clear_cache_specific_confirm(cache_manager: CacheManager, mock_settings):
    db_path = mock_settings.sqlite_file
    cache_manager.update_cache(CacheType.QUICK, {"test": "data"})

    result = runner.invoke(app, ["clear", "quick", "--db-path", str(db_path)], input="y\n")

    assert result.exit_code == 0
    assert "Successfully cleared 1 entries from the Quick cache" in result.stdout


def test_clear_cache_no_cache_type(cache_manager: CacheManager, mock_settings):
    db_path = mock_settings.sqlite_file
    cache_manager.update_cache(CacheType.QUICK, {"test": "data"})
    result = runner.invoke(app, ["clear", "--db-path", str(db_path)])

    assert result.exit_code == 1
    assert "Please specify a cache to clear" in result.stdout


def test_clear_cache_empty(cache_manager: CacheManager, mock_settings):
    db_path = mock_settings.sqlite_file
    result = runner.invoke(app, ["clear", "quick", "--force", "--db-path", str(db_path)])

    assert result.exit_code == 0
    assert "No entries found for quick cache" in result.stdout
