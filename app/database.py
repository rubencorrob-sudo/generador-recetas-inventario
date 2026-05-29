from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    ensure_recipe_columns()


def ensure_recipe_columns() -> None:
    inspector = inspect(engine)
    if "recipes" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("recipes")}
    columns = {
        "description": "TEXT",
        "servings": "INTEGER",
        "missing_ingredients": "JSON",
        "tips": "JSON",
        "nutrition": "JSON",
        "tags": "JSON",
        "is_favorite": "BOOLEAN",
    }
    missing = [(name, column_type) for name, column_type in columns.items() if name not in existing]
    if not missing:
        return

    with engine.begin() as connection:
        for name, column_type in missing:
            connection.exec_driver_sql(
                f"ALTER TABLE recipes ADD COLUMN {name} {column_type}"
            )
