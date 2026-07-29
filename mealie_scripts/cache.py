import logging
from enum import Enum
from pathlib import Path

from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import String, create_engine, delete, func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

logger = logging.getLogger(__name__)


class CacheType(Enum):
    MACROS = "macros"
    QUICK = "quick"


CACHE_DESCRIPTIONS: dict[CacheType, str] = {
    CacheType.MACROS: "Recipes that have already had macro tags checked and added.",
    CacheType.QUICK: "Recipes that have already had the quick tag checked and added.",
}


class Base(DeclarativeBase):
    pass


class ProcessedRecipe(Base):
    __tablename__ = "processed_recipes"

    cache_type: Mapped[CacheType] = mapped_column(SQLAlchemyEnum(CacheType), primary_key=True)
    recipe_id: Mapped[str] = mapped_column(String, primary_key=True)


class CacheManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self._init_db()

    def _init_db(self) -> None:
        """Create tables if they don't already exist."""
        Base.metadata.create_all(self.engine)

    def is_cached(self, cache_type: CacheType, recipe_id: str) -> bool:
        """Check if a single recipe has already been processed."""
        stmt = select(ProcessedRecipe).where(
            ProcessedRecipe.cache_type == cache_type.name,
            ProcessedRecipe.recipe_id == recipe_id,
        )
        with Session(self.engine) as session:
            return session.scalar(stmt) is not None

    def load_cache(self, cache_type: CacheType) -> set[str]:
        """Fetch all cached recipe IDs for a given cache."""
        stmt = select(ProcessedRecipe.recipe_id).where(ProcessedRecipe.cache_type == cache_type.name)
        with Session(self.engine) as session:
            return set(session.scalars(stmt).all())

    def add_to_cache(self, cache_type: CacheType, recipe_ids: set[str] | list[str]) -> None:
        """Atomically insert new recipe IDs into the cache, ignoring duplicates."""
        if not recipe_ids:
            return

        values = [{"cache_type": cache_type.name, "recipe_id": r_id} for r_id in recipe_ids]
        stmt = insert(ProcessedRecipe).values(values).on_conflict_do_nothing()

        with Session(self.engine) as session:
            session.execute(stmt)
            session.commit()

    def get_cache_counts(self) -> dict[CacheType, int]:
        """Return a dict of each cache type and the number of entries."""

        counts = {cache_type: 0 for cache_type in CacheType}

        stmt = select(ProcessedRecipe.cache_type, func.count(ProcessedRecipe.recipe_id)).group_by(
            ProcessedRecipe.cache_type
        )

        with Session(self.engine) as session:
            for cache_type, count in session.execute(stmt):
                counts[CacheType(cache_type)] = count

        return counts

    def clear_cache(self, cache_type: CacheType | None = None) -> int:
        """
        Clears entries from the cache.

        Args:
            cache_type: The cache to clear. If None, all caches are cleared.

        Returns:
            The number of rows deleted.
        """
        if cache_type:
            stmt = delete(ProcessedRecipe).where(ProcessedRecipe.cache_type == cache_type.name)
        else:
            stmt = delete(ProcessedRecipe)

        with Session(self.engine) as session:
            result = session.execute(stmt)
            session.commit()
            return result.rowcount or 0
