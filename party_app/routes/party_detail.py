from datetime import date, time
from uuid import UUID

from fastapi import APIRouter, Depends, Request, Form, status
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse
from sqlmodel import Session

from party_app.dependency import Templates, get_session
from party_app.models import Party

router = APIRouter(prefix="/party", tags=["party"])


@router.get("/{party_id}", name="party_detail_page", response_class=HTMLResponse)
def party_detail_page(
    party_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
):
    party = session.get(Party, party_id)

    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Party not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="party_detail/page_party_detail.html",
        context={"party": party},
    )


@router.put(
    "/{party_id}", name="party_detail_save_form_partial", response_class=HTMLResponse
)
def party_detail_save_form_partial(
    party_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
    party_date: date = Form(...),
    party_time: time = Form(...),
    invitation: str = Form(...),
    venue: str = Form(...),
):
    party = session.get(Party, party_id)

    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Party not found"
        )

    party.party_date = party_date
    party.party_time = party_time
    party.invitation = invitation
    party.venue = venue

    session.add(party)
    session.commit()
    session.refresh(party)

    return templates.TemplateResponse(
        request=request,
        name="party_detail/partial_party_edit.html",
        context={"party": party},
    )


@router.get(
    "/{party_id}/edit", name="partial_party_detail_edit", response_class=HTMLResponse
)
def party_detail_form_partial(
    party_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
):
    party = session.get(Party, party_id)

    if not party:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Party not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="party_detail/partial_party_edit.html",
        context={"party": party},
    )
