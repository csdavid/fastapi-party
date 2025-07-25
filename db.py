import os
from pathlib import Path

from sqlmodel import create_engine


# database_file_path = Path(__file__).resolve().parent.absolute() / "database.db"
# print(database_file_path)
# engine = create_engine(f"sqlite:///{database_file_path}")
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{Path(__file__).parent / 'database.db'}"
).replace("postgres://", "postgresql+psycopg://", 1)
engine = create_engine(DATABASE_URL)
