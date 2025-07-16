import os
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _load_config_url() -> str | None:
    """Return ``database_url`` from config.yaml if available."""
    config_path = os.getenv("CONFIG_PATH", "config.yaml")
    try:
        with open(config_path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh) or {}
        return config.get("database_url")
    except Exception:
        return None


DATABASE_URL = os.getenv("DATABASE_URL") or _load_config_url() or (
    "postgresql+psycopg2://postgres:postgres@db/postgres"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
