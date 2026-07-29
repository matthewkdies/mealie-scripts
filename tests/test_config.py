from mealie_scripts.config import Settings


# Add a test for SecretStr handling
def test_settings_secret_str_handling():
    test_token = "my_secret_token_123"
    settings = Settings(mealie_api_token=test_token)
    assert settings.mealie_api_token.get_secret_value() == test_token
    assert str(settings.mealie_api_token) == "**********"  # Pydantic's default repr for SecretStr
