from datetime import date, datetime

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from party_app.dependency import get_session
from party_app.main import app
from party_app.models import Party, Gift, Guest


@pytest.fixture(scope="session", name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def create_party():
    def _create_party(session: Session, **kwargs):
        party = Party(
            party_date=kwargs.get("party_date", date.today()),
            party_time=kwargs.get(
                "party_time", datetime.strptime("12:00", "%H:%M").time()
            ),
            venue=kwargs.get("venue", "Amazing castle"),
            invitation=kwargs.get("invitation", "You are invited to the party!"),
        )
        session.add(party)
        session.commit()
        session.refresh(party)
        return party

    return _create_party


@pytest.fixture(scope="session")
def create_gift():
    def _create_gift(session: Session, party, **kwargs):
        gift = Gift(
            gift=kwargs.get("gift", "Test gift"),
            price=kwargs.get("price", 12.5),
            link=kwargs.get("link", "https://testlink.com"),
            party=party,
        )
        session.add(gift)
        session.commit()
        session.refresh(gift)
        return gift

    return _create_gift


@pytest.fixture(scope="session")
def create_guest():
    def _create_guest(session: Session, party, **kwargs):
        guest = Guest(
            name=kwargs.get("name", "Anna Boleyn"),
            attending=kwargs.get("attending", True),
            party=party,
        )
        session.add(guest)
        session.commit()
        session.refresh(guest)
        return guest

    return _create_guest
