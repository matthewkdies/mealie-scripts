from enum import Enum


class CacheType(Enum):
    MACROS = "macros"
    QUICK = "quick"


CACHE_DESCRIPTIONS: dict[CacheType, str] = {
    CacheType.MACROS: "Recipes that have already had macro tags checked and added.",
    CacheType.QUICK: "Recipes that have already had the quick tag checked and added.",
}
