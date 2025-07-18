from datetime import datetime
from typing import Callable

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from party_app.main import app
from party_app.models import Party


def test_party_detail_page_returns_party_detail(
    session: Session, client: TestClient, create_party: Callable[..., Party]
):
    party = create_party(session=session)

    url = app.url_path_for("party_detail_page", party_id=party.uuid)
    print("*******************************************************")
    print("url:", url)
    print("*******************************************************")
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.context["party"] == party


def test_party_detail_form_partial_returns_a_form_with_party_details(
    session: Session, client: TestClient, create_party: Callable[..., Party]
):
    party = create_party(session=session)

    url = app.url_path_for("partial_party_detail_edit", party_id=party.uuid)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.context["party"] == party
    assert "party-form" in response.text


def test_party_detail_form_partial_updates_party_and_returns_updated_party(
    session: Session, client: TestClient, create_party: Callable[..., Party]
):
    party = create_party(session=session)

    url = app.url_path_for("party_detail_save_form_partial", party_id=party.uuid)
    updated_data = {
        "party_date": "2030-01-01",
        "party_time": "00:00",
        "invitation": "Updated invitation",
        "venue": "Updated Venue",
    }
    response = client.put(url, data=updated_data)

    session.refresh(party)

    assert response.status_code == status.HTTP_200_OK
    assert (
        party.party_date
        == datetime.strptime(updated_data["party_date"], "%Y-%m-%d").date()
    )
    assert (
        party.party_time
        == datetime.strptime(updated_data["party_time"], "%H:%M").time()
    )
    assert party.invitation == updated_data["invitation"]
    assert party.venue == updated_data["venue"]
