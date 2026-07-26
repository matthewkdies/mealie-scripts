import json
import logging

from .config import settings

logger = logging.getLogger(__name__)


def load_cache(command_name: str) -> set[str]:
    cache_file = settings.get_cache_file(command_name)
    if not cache_file.exists():
        return set()
    with open(cache_file, "r") as f:
        try:
            return set(json.load(f))
        except json.JSONDecodeError:
            logger.warning("Error getting cache from '%s'. Continuing without cache.", str(cache_file))
            return set()


def save_cache(command_name: str, cache_set: set[str]) -> None:
    cache_file = settings.get_cache_file(command_name)
    with open(cache_file, "w") as f:
        json.dump(list(cache_set), f)
