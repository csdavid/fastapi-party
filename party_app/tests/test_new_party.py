from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from party_app.main import app
from party_app.models import Party


def test_new_party_form_includes_form(client: TestClient):
    url = app.url_path_for("new_party_form_page")

    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert "new-party-form" in response.text


def test_create_party(session: Session, client: TestClient):
    url = app.url_path_for("new_party_create_page")

    data = {
        "party_date": "2025-06-06",
        "party_time": "18:00:00",
        "venue": "My venue",
        "invitation": "Come to my party!",
    }

    response = client.post(url, data=data, follow_redirects=False)

    assert response.status_code == status.HTTP_302_FOUND
    assert len(session.exec(select(Party)).all()) == 1


def test_validate_date(client: TestClient):
    url = app.url_path_for("validate_date_partial")

    data = {"party_date": "2021-06-06"}

    response = client.post(url, data=data)
    assert response.text == "You chose a date in the past."


def test_validate_invitation(client: TestClient):
    url = app.url_path_for("validate_invitation_partial")

    data = {
        "invitation": "Short",
    }

    response = client.post(url, data=data)

    assert response.text == "You really should write an invitation."
