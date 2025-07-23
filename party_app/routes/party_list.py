from datetime import date

from fastapi import APIRouter, Depends, Request, Query
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select, func

from party_app.dependency import Templates, get_session
from party_app.models import Party

router = APIRouter(prefix="", tags=["parties"])

_PAGE_SIZE = 6


@router.get("/", name="party_list_page", response_class=HTMLResponse)
def party_list_page(
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1),
):
    today = date.today()

    num_all_parties = session.exec(
        select(func.count(Party.uuid)).where(Party.party_date >= today)
    ).one()
    offset = (page - 1) * _PAGE_SIZE

    parties = session.exec(
        select(Party).where(Party.party_date >= today).offset(offset).limit(_PAGE_SIZE)
    ).all()

    next_page = page + 1 if (offset + _PAGE_SIZE) <= num_all_parties else None

    htmx_request = request.headers.get("HX-Request", None)

    if htmx_request:
        template_name = "party_list/partial_party_list.html"
    else:
        template_name = "party_list/page_party_list.html"

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={"parties": parties, "next_page": next_page},
    )
