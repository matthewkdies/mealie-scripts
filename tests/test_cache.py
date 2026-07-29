from mealie_scripts.cache import CacheManager, CacheType
from mealie_scripts.config import Settings


def test_cache_manager_init(cache_manager: CacheManager, mock_settings: Settings):
    """Ensure the database file and table are created on initialization."""
    assert mock_settings.sqlite_file.exists()
    assert cache_manager.get_cache_counts() == {CacheType.MACROS: 0, CacheType.QUICK: 0}


def test_add_and_is_cached(cache_manager: CacheManager):
    """Test adding recipe IDs to the cache and checking if they exist."""
    recipe_ids = {"recipe-1", "recipe-2"}
    cache_type = CacheType.QUICK

    cache_manager.add_to_cache(cache_type, recipe_ids)

    assert cache_manager.is_cached(cache_type, "recipe-1")
    assert cache_manager.is_cached(cache_type, "recipe-2")
    assert not cache_manager.is_cached(cache_type, "recipe-3")
    assert not cache_manager.is_cached(CacheType.MACROS, "recipe-1")


def test_add_to_cache_duplicates(cache_manager: CacheManager):
    """Test that adding duplicate recipe IDs doesn't raise an error and they are ignored."""
    recipe_ids = ["recipe-1", "recipe-1", "recipe-2"]
    cache_type = CacheType.QUICK

    cache_manager.add_to_cache(cache_type, recipe_ids)
    assert cache_manager.load_cache(cache_type) == {"recipe-1", "recipe-2"}
    counts = cache_manager.get_cache_counts()
    assert counts[CacheType.QUICK] == 2


def test_load_cache(cache_manager: CacheManager):
    """Test loading all cached recipe IDs for a specific cache type."""
    macros_ids = {"m-recipe-1", "m-recipe-2"}
    quick_ids = {"q-recipe-1"}
    cache_manager.add_to_cache(CacheType.MACROS, macros_ids)
    cache_manager.add_to_cache(CacheType.QUICK, quick_ids)

    loaded_macros = cache_manager.load_cache(CacheType.MACROS)
    assert loaded_macros == macros_ids

    loaded_quick = cache_manager.load_cache(CacheType.QUICK)
    assert loaded_quick == quick_ids


def test_get_cache_counts(cache_manager: CacheManager):
    """Test getting the counts of items in each cache."""
    cache_manager.add_to_cache(CacheType.MACROS, ["m1", "m2", "m3"])
    cache_manager.add_to_cache(CacheType.QUICK, ["q1"])

    counts = cache_manager.get_cache_counts()

    assert counts[CacheType.MACROS] == 3
    assert counts[CacheType.QUICK] == 1


def test_clear_cache_specific(cache_manager: CacheManager):
    """Test clearing a specific cache type."""
    cache_manager.add_to_cache(CacheType.MACROS, ["m1", "m2"])
    cache_manager.add_to_cache(CacheType.QUICK, ["q1"])

    deleted_rows = cache_manager.clear_cache(CacheType.MACROS)
    assert deleted_rows == 2

    counts = cache_manager.get_cache_counts()
    assert counts[CacheType.MACROS] == 0
    assert counts[CacheType.QUICK] == 1
    assert not cache_manager.is_cached(CacheType.MACROS, "m1")
    assert cache_manager.is_cached(CacheType.QUICK, "q1")


def test_clear_cache_all(cache_manager: CacheManager):
    """Test clearing all caches."""
    cache_manager.add_to_cache(CacheType.MACROS, ["m1", "m2"])
    cache_manager.add_to_cache(CacheType.QUICK, ["q1"])

    deleted_rows = cache_manager.clear_cache()
    assert deleted_rows == 3

    counts = cache_manager.get_cache_counts()
    assert counts[CacheType.MACROS] == 0
    assert counts[CacheType.QUICK] == 0
    assert not cache_manager.load_cache(CacheType.MACROS)
    assert not cache_manager.load_cache(CacheType.QUICK)


def test_add_to_cache_empty_list(cache_manager: CacheManager):
    """Test that adding an empty list does not cause an error."""
    cache_type = CacheType.QUICK
    cache_manager.add_to_cache(cache_type, [])
    assert cache_manager.load_cache(cache_type) == set()
    counts = cache_manager.get_cache_counts()
    assert counts[CacheType.QUICK] == 0
