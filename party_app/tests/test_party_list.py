import datetime
from typing import Callable

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from party_app.main import app
from party_app.models import Party


def test_party_list_page_returns_list_of_future_parties(
    session: Session, client: TestClient, create_party: Callable[..., Party]
):
    today = datetime.date.today()

    valid_party = create_party(
        session=session, party_date=today + datetime.timedelta(days=1), venue="Venue 1"
    )

    create_party(
        session=session,
        party_date=today - datetime.timedelta(days=10),
        venue="Venue 2",
    )

    url = app.url_path_for("party_list_page")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.context["parties"]) == 1
    assert response.context["parties"] == [valid_party]
