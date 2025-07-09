import json
from datetime import datetime
from pathlib import Path
from uuid import UUID
from db import engine
from party_app.models import Gift, Guest, Party

from sqlmodel import Session, SQLModel


def clear_all_tables():
    """Clear all data from the tables."""
    with Session(engine) as session:
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(table.delete())
        session.commit()


def load_initial_data_party(json_file, model):
    """Load Party data with special handling for date and time fields."""
    with open(json_file, "r") as file:
        data = json.load(file)

        with Session(engine) as session:
            for item in data:
                try:
                    item["party_date"] = datetime.strptime(
                        item["party_date"], "%Y-%m-%d"
                    ).date()
                    item["party_time"] = datetime.strptime(
                        item["party_time"], "%H:%M:%S"
                    ).time()
                    item["uuid"] = UUID(item["uuid"])

                    new_instance = model(**item)
                    session.add(new_instance)
                except Exception as e:
                    print(f"Error adding {item} to {model.__name__}: {e}")

            session.commit()
            print(f"Data from {json_file} loaded successfully into {model.__name__}.")


def load_initial_data_party_child(json_file, model):
    """Load data from a JSON file into the specified database model."""
    with open(json_file, "r") as file:
        data = json.load(file)

        with Session(engine) as session:
            for item in data:
                try:
                    item["uuid"] = UUID(item["uuid"])
                    item["party_id"] = UUID(item["party_id"])
                    new_instance = model(**item)
                    session.add(new_instance)
                except Exception as e:
                    print(f"Error adding {item} to {model.__name__}: {e}")

            session.commit()
            print(f"Data from {json_file} loaded successfully into {model.__name__}.")


if __name__ == "__main__":
    clear_all_tables()
    load_initial_data_party(
        Path(__file__).parent.absolute() / "initial_parties.json", Party
    )
    load_initial_data_party_child(
        Path(__file__).parent.absolute() / "initial_gifts.json", Gift
    )
    load_initial_data_party_child(
        Path(__file__).parent.absolute() / "initial_guests.json", Guest
    )
