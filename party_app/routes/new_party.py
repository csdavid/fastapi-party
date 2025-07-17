from datetime import date
from typing import Annotated

from fastapi import APIRouter, Request, Depends, Form, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session

from party_app.dependency import Templates, get_session
from party_app.models import Party, PartyForm

router = APIRouter(prefix="/party/new", tags=["new_party"])


@router.get("/", name="new_party_form_page", response_class=HTMLResponse)
def new_party_form_page(request: Request, templates: Templates):
    return templates.TemplateResponse(
        request=request,
        name="new_party/page_new_party.html",
    )


@router.post("/", name="new_party_create_page", response_class=HTMLResponse)
def new_party_create_page(
    request: Request,
    party_form: Annotated[PartyForm, Form()],
    session: Session = Depends(get_session),
):
    party = Party(**party_form.model_dump())

    session.add(party)
    session.commit()
    session.refresh(party)

    return RedirectResponse(
        request.url_for("party_detail_page", party_id=party.uuid),
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/validate_date", name="validate_date_partial", response_class=Response)
def validate_date(
    party_date: date = Form(...),
):
    if party_date < date.today():
        return HTMLResponse(
            content="You chose a date in the past.", status_code=status.HTTP_200_OK
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "validate_date", name="validate_invitation_partial", response_class=Response
)
def validate_invitation(
    invitation: str = Form(...),
):
    if len(invitation.strip()) < 10:
        return HTMLResponse(
            content="You really should write an invitation.",
            status_code=status.HTTP_200_OK,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
