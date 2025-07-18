from decimal import Decimal
from typing import Callable

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from party_app.main import app
from party_app.models import Party, Gift


def test_gift_registry_page_lists_gifts_for_party_by_id(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_gift: Callable[..., Gift],
):
    party = create_party(session=session)
    gift_1 = create_gift(session=session, gift="Roses", party=party)
    gift_2 = create_gift(session=session, gift="Chocolate", party=party)

    another_party = create_party(session=session, venue="Another Venue")
    create_gift(session=session, party=another_party)

    url = app.url_path_for("gift_registry_page", party_id=party.uuid)
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.context["gifts"] == [gift_1, gift_2]
    assert response.context["party"] == party


def test_gift_detail_partial_returns_gift_detail_including_party(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_gift: Callable[..., Gift],
):
    party = create_party(session=session)
    gift = create_gift(session=session, party=party)

    url = app.url_path_for(
        "gift_detail_partial", party_id=party.uuid, gift_id=gift.uuid
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.context["gift"] == gift
    assert response.context["party"] == party


def test_gift_update_save_partial_returns_gift_update_form_including_party_id(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_gift: Callable[..., Gift],
):
    party = create_party(session=session)
    gift = create_gift(session=session, party=party)

    url = app.url_path_for(
        "gift_update_partial", party_id=party.uuid, gift_id=gift.uuid
    )
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.context["gift"] == gift
    assert response.context["party_id"] == party.uuid
    assert "update-gift-form" in response.text


def test_gift_update_save_partial_updates_gift_and_returns_its_details_including_party(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_gift: Callable[..., Gift],
):
    party = create_party(session=session)
    gift = create_gift(session=session, party=party)

    url = app.url_path_for(
        "gift_update_save_partial", party_id=party.uuid, gift_id=gift.uuid
    )
    updated_data = {
        "gift_name": "Updated gift",
        "price": "50",
        "link": "https://updatedtestlink.com",
    }
    response = client.put(url, data=updated_data)

    session.refresh(gift)

    assert response.status_code == status.HTTP_200_OK
    assert gift.gift_name == updated_data["gift_name"]
    assert gift.price == Decimal(updated_data["price"])
    assert gift.link == updated_data["link"]
    assert gift.party_id == party.uuid
    assert response.context["party"] == party


def test_partial_gift_delete_removes_gift(
    session: Session,
    client: TestClient,
    create_party: Callable[..., Party],
    create_gift: Callable[..., Gift],
):
    party = create_party(session=session)
    gift = create_gift(session=session, party=party)

    assert len(session.exec(select(Gift).where(Gift.party_id == party.uuid)).all()) == 1

    url = app.url_path_for(
        "gift_remove_partial", party_id=party.uuid, gift_id=gift.uuid
    )
    client.delete(url)

    assert len(session.exec(select(Gift).where(Gift.party_id == party.uuid)).all()) == 0
