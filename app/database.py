import json
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base, Task, ContentType
from config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)


def load_tasks(tasks_path: str = "data/tasks.json") -> int:
    """Load tasks from JSON into the database if not present.

    Returns number of tasks inserted.
    """
    path = Path(tasks_path)
    if not path.exists():
        raise FileNotFoundError(f"Tasks file not found: {tasks_path}")

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    tasks = data.get("tasks", [])
    inserted = 0
    with SessionLocal() as db:
        for t in tasks:
            if db.get(Task, t["id"]) is None:
                db.add(
                    Task(
                        id=t["id"],
                        content_type=ContentType(t["content_type"]),
                        title=t.get("title"),
                        description=t.get("description"),
                        structured_prompt=t.get("structured_prompt"),
                        example_prompt_template=t.get("example_prompt_template"),
                    )
                )
                inserted += 1
        db.commit()
    return inserted

