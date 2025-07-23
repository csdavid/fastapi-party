from typing import Callable

import pytest

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


def test_search_guests(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_guest: Callable[..., Guest],
):
    party = create_party(session=session)
    another_party = create_party(session=session, venue="Another Venue")

    create_guest(session=session, party=party, name="Anna")
    create_guest(session=session, party=party, name="Catherine")
    create_guest(session=session, party=another_party, name="Anna")

    url = app.url_path_for("filter_guests_partial", party_id=party.uuid)
    data = {"guest_search": "An"}

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.context["guests"]) == 1
    assert response.context["guests"][0].name == "Anna"


@pytest.mark.parametrize(
    "guest_attending_status,  search_text, attending_filter, expected_number_of_filtered_guests",
    [
        (True, "an", "all", 1),  # should pass, this is the same as before
        (True, "be", "all", 0),  # should pass, this is the same as before
        (True, "be", "attending", 0),  # should pass since search doesn't match
        (True, "be", "not_attending", 0),  # should pass since search doesn't match
        (
            True,
            "an",
            "attending",
            1,
        ),  # should pass since search matches and status isn't checked
        (
            True,
            "an",
            "not_attending",
            0,
        ),  # should fail since search matches but filter doesn't
        (True, "", "attending", 1),  # should pass since empty search matches the result
        (
            True,
            "",
            "not_attending",
            0,
        ),  # should fail, since search matches, but filter doesn't
        (False, "an", "all", 1),  # should pass since filter is "all"
        (False, "be", "all", 0),  # should pass since filter is "all"
        (False, "be", "attending", 0),  # should pass since search doesn't match
        (False, "be", "not_attending", 0),  # should pass since search doesn't match
        (
            False,
            "an",
            "attending",
            0,
        ),  # should fail since "an" matches, but "attending" shouldn't
        (
            False,
            "an",
            "not_attending",
            1,
        ),  # should pass since filter matches even if not checked
        (False, "", "attending", 0),  # should fail since filter doesn't match output
        (
            False,
            "",
            "not_attending",
            1,
        ),  # should pass since filter matches output even if not checked
    ],
)
def test_filter_guest_by_status_and_search(
    guest_attending_status,
    search_text,
    attending_filter,
    expected_number_of_filtered_guests,
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_guest: Callable[..., Guest],
):
    party = create_party(session=session)
    create_guest(
        session=session, party=party, name="Anna", attending=guest_attending_status
    )

    another_party = create_party(session=session, venue="Another venue")
    create_guest(session=session, party=another_party, name="Anna")

    url = app.url_path_for("filter_guests_partial", party_id=party.uuid)
    data = {"guest_search": search_text, "attending_filter": attending_filter}

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.context["guests"]) == expected_number_of_filtered_guests
