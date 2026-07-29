import logging
from pathlib import Path
from typing import overload

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


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

    # sqlite storage
    sqlite_file: Path = Path.home() / ".config/mealie_scripts/mealie_scripts.db"

    # Rate Limiting
    sleep_between_requests: float = 1.5

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MEALIE_SCRIPTS_")


settings = Settings()
