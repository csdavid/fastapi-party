from typing import Callable

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from party_app.main import app
from party_app.models import Guest, Party


# Test for the guest list page of a party
def test_guest_list_page_lists_guests_for_party_by_id(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_guest: Callable[..., Guest],
):
    party = create_party(session=session)
    guest_1 = create_guest(session=session, name="Alice", party=party)
    guest_2 = create_guest(session=session, name="Bob", party=party)

    another_party = create_party(session=session, venue="Another Venue")
    create_guest(session=session, party=another_party)

    url = app.url_path_for("guest_list_page", party_id=party.uuid)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert list(response.context["guests"]) == [guest_1, guest_2]
    assert response.context["party_id"] == party.uuid


# Test for marking a guest as attending
def test_mark_guests_attending_updates_guests_returns_whole_list(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_guest: Callable[..., Guest],
):
    party = create_party(session=session)
    guest_1 = create_guest(session=session, party=party, attending=False)
    guest_2 = create_guest(session=session, party=party, attending=False)

    url = app.url_path_for(
        "mark_guests_attending_partial",
        party_id=party.uuid,
    )

    response = client.put(url, data={"guest_ids": [guest_1.uuid]})

    session.refresh(guest_1)
    session.refresh(guest_2)

    assert guest_1.attending is True
    assert guest_2.attending is False

    assert response.status_code == status.HTTP_200_OK
    assert response.context["guests"] == [guest_1, guest_2]


# Test for marking a guest as not attending
def test_mark_guests_not_attending_updates_guests_returns_whole_list(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_guest: Callable[..., Guest],
):
    party = create_party(session=session)
    guest_1 = create_guest(session=session, party=party, attending=True)
    guest_2 = create_guest(session=session, party=party, attenging=True)

    url = app.url_path_for(
        "mark_guests_not_attending_partial",
        party_id=party.uuid,
    )

    response = client.put(url, data={"guest_ids": [guest_1.uuid]})

    session.refresh(guest_1)
    session.refresh(guest_2)

    assert guest_1.attending is False
    assert guest_2.attending is True

    assert response.status_code == status.HTTP_200_OK
    assert response.context["guests"] == [guest_1, guest_2]
