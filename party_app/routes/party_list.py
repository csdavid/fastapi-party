from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from party_app.dependency import Templates, get_session
from party_app.models import Party

router = APIRouter(prefix="", tags=["parties"])


@router.get("/", name="party_list_page", response_class=HTMLResponse)
def party_list_page(
    request: Request, templates: Templates, session: Session = Depends(get_session)
):
    today = date.today()
    parties = session.exec(select(Party).where(Party.party_date >= today)).all()

    return templates.TemplateResponse(
        request=request,
        name="party_list/page_party_list.html",
        context={"parties": parties},
    )
