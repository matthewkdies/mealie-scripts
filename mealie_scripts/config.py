import logging
from pathlib import Path
from typing import Annotated, overload

from pydantic import AfterValidator, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def validate_config_dir(config_dir: Path) -> Path:
    config_dir = config_dir.expanduser()

    if not config_dir.is_dir():
        logger.info("Config dir at '%s' does not exist. Attempting to create.", config_dir)
        config_dir.mkdir(parents=False, exist_ok=False)

    return config_dir


class Settings(BaseSettings):
    @overload
    def __init__(self, *, api_key: str | SecretStr, **kwargs): ...

    @overload
    def __init__(self, **kwargs): ...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    mealie_url: str = "https://mealie.fixme.dne"
    mealie_api_token: SecretStr = SecretStr("your_api_token_here")

    # Thresholds
    protein_threshold: float = 22.0
    fiber_threshold: float = 10.0
    quick_threshold_minutes: int = 30

    # Tag Names
    protein_tag_name: str = "High protein"
    fiber_tag_name: str = "High fiber"
    quick_tag_name: str = "Quick"

    # persistent storage
    config_dir: Annotated[Path, AfterValidator(validate_config_dir)] = Path.home() / ".config/mealie_scripts"

    # Rate Limiting
    sleep_between_requests: float = 1.5

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MEALIE_SCRIPTS_")

    def get_cache_file(self, command_name: str) -> Path:
        return self.config_dir / f"{command_name}.json"


settings = Settings()
