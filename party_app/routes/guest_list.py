from uuid import UUID

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from party_app.dependency import Templates, get_session
from party_app.models import Guest, Party

router = APIRouter(prefix="/party/{party_id}/guests", tags=["guest"])


# returns the guest list page for a specific party
@router.get("/", name="guest_list_page", response_class=HTMLResponse)
def guest_list_page(
    party_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
):
    guests = session.exec(select(Guest).where(Guest.party_id == party_id)).all()

    return templates.TemplateResponse(
        request=request,
        name="guest_list/page_guest_list.html",
        context={"party_id": party_id, "guests": guests},
    )


@router.put(
    "/mark-attending", name="mark_guests_attending_partial", response_class=HTMLResponse
)
def mark_guests_attending_partial(
    party_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
    guest_ids: list[UUID] = Form(...),
):
    attending_guests = session.exec(
        select(Guest).where(Guest.uuid.in_(guest_ids))
    ).all()

    for guest in attending_guests:
        guest.attending = True

    session.commit()

    guests = session.exec(select(Guest).where(Guest.party_id == party_id)).all()

    return templates.TemplateResponse(
        request=request,
        name="guest_list/partial_guest_filter_and_list.html",
        context={"party_id": party_id, "guests": guests},
    )


@router.put(
    "/mark-not-attending",
    name="mark_guests_not_attending_partial",
    response_class=HTMLResponse,
)
def mark_guests_not_attending_partial(
    party_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
    guest_ids: list[UUID] = Form(...),
):
    not_attending_guests = session.exec(
        select(Guest).where(Guest.uuid.in_(guest_ids))
    ).all()

    for guest in not_attending_guests:
        guest.attending = False

    session.commit()

    guests = session.exec(select(Guest).where(Guest.party_id == party_id)).all()

    return templates.TemplateResponse(
        request=request,
        name="guest_list/partial_guest_filter_and_list.html",
        context={"party_id": party_id, "guests": guests},
    )


def filter_attending(session: Session, party_id: UUID, **kwargs) -> list[Guest]:
    return session.exec(
        select(Guest).where((Guest.party_id == party_id) & (Guest.attending == True))
    ).all()


def filter_not_attending(session: Session, party_id: UUID, **kwargs) -> list[Guest]:
    return session.exec(
        select(Guest).where((Guest.party_id == party_id) & (Guest.attending == False))
    ).all()


def filter_attending_and_search(
    session: Session, party_id: UUID, **kwargs
) -> list[Guest]:
    search_text = kwargs.get("search_text", "")
    return session.exec(
        select(Guest).where(
            (Guest.party_id == party_id)
            & (Guest.attending == True)
            & (Guest.name.ilike(f"%{search_text}%"))
        )
    ).all()


def filter_not_attending_and_search(
    session: Session, party_id: UUID, **kwargs
) -> list[Guest]:
    search_text = kwargs.get("search_text", "")
    return session.exec(
        select(Guest).where(
            (Guest.party_id == party_id)
            & (Guest.attending == False)
            & (Guest.name.ilike(f"%{search_text}%"))
        )
    ).all()


def filter_search(session: Session, party_id: UUID, **kwargs) -> list[Guest]:
    search_text = kwargs.get("search_text", "")
    return session.exec(
        select(Guest).where(
            (Guest.party_id == party_id) & (Guest.name.ilike(f"%{search_text}%"))
        )
    ).all()


def filter_default(session: Session, party_id: UUID, **kargs) -> list[Guest]:
    return session.exec(select(Guest).where(Guest.party_id == party_id)).all()


QUERY_FILTERS = {
    ("attending", False): filter_attending,
    ("not_attending", False): filter_not_attending,
    ("attending", True): filter_attending_and_search,
    ("not_attending", True): filter_not_attending_and_search,
    ("all", True): filter_search,
}


@router.post("/filter", name="filter_guests_partial", response_class=HTMLResponse)
def filter_guests_partial(
    party_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
    guest_search: str = Form(...),
    attending_filter: str = Form(...),
):
    query_filter = QUERY_FILTERS.get(
        (attending_filter, bool(guest_search)), filter_default
    )

    guests = query_filter(session=session, party_id=party_id, search_text=guest_search)

    return templates.TemplateResponse(
        request=request,
        name="guest_list/partial_guest_list.html",
        context={"party_id": party_id, "guests": guests},
    )
