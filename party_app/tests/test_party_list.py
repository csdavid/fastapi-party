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


def test_party_list_page_returns_paginated_response(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
):
    for i in range(11):
        create_party(
            session=session,
            venue=f"Venue {i + 1}",
        )

    url = app.url_path_for("party_list_page")

    response_first_page = client.get(url)
    assert response_first_page.status_code == status.HTTP_200_OK
    assert len(response_first_page.context["parties"]) == 6

    response_second_page = client.get(f"{url}?page=2")
    assert response_second_page.status_code == status.HTTP_200_OK
    assert len(response_second_page.context["parties"]) == 5


def test_party_list_page_returns_correct_template(
    session: Session, client: TestClient, create_party: Callable[..., Party]
):
    create_party(session=session)

    url = app.url_path_for("party_list_page")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.template.name == "party_list/page_party_list.html"

    htmx_response = client.get(url, headers={"HX-Request": "true"})
    assert htmx_response.status_code == status.HTTP_200_OK
    assert htmx_response.template.name == "party_list/partial_party_list.html"
