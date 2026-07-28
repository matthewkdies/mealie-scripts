from pathlib import Path

from mealie_scripts.config import Settings, validate_config_dir


def test_validate_config_dir_exists(tmp_path):
    test_dir = tmp_path / "existing_dir"
    test_dir.mkdir()
    result = validate_config_dir(test_dir)
    assert result == test_dir
    assert result.is_dir()


def test_validate_config_dir_creates_new_dir(tmp_path):
    test_dir = tmp_path / "new_dir"
    assert not test_dir.is_dir()
    result = validate_config_dir(test_dir)
    assert result == test_dir
    assert result.is_dir()


def test_validate_config_dir_expands_user(tmp_path, monkeypatch):
    expected_expanded_path = tmp_path / ".config/test_config_dir"
    expected_expanded_path.parent.mkdir(parents=True, exist_ok=True)

    assert not expected_expanded_path.exists()
    result = validate_config_dir(expected_expanded_path)
    assert result == expected_expanded_path
    assert result.is_dir()  # assert that it was created


def test_settings_get_cache_file(tmp_path):
    # Use tmp_path for config_dir to avoid polluting user's home directory
    # and to ensure a known path for testing.
    settings = Settings(config_dir=tmp_path)
    cache_file = settings.get_cache_file("test_command")
    assert cache_file == tmp_path / "test_command.json"
    assert isinstance(cache_file, Path)


# Add a test for SecretStr handling
def test_settings_secret_str_handling():
    test_token = "my_secret_token_123"
    settings = Settings(mealie_api_token=test_token)
    assert settings.mealie_api_token.get_secret_value() == test_token
    assert str(settings.mealie_api_token) == "**********"  # Pydantic's default repr for SecretStr
