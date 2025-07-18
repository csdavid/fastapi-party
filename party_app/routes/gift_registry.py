from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from party_app.dependency import Templates, get_session
from party_app.models import Gift, Party, GiftForm

router = APIRouter(prefix="/party/{party_id}/gifts", tags=["gifts"])


# Regresa la lista de regalos para una fiesta específica
@router.get("/", name="gift_registry_page", response_class=HTMLResponse)
def gift_registry_page(
    party_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
):
    party = session.get(Party, party_id)
    gifts = session.exec(select(Gift).where(Gift.party_id == party_id)).all()

    return templates.TemplateResponse(
        request=request,
        name="gift_registry/page_gift_registry.html",
        context={"party": party, "gifts": gifts},
    )


# Regresa el detalle para un regalo específico
@router.get("/{gift_id}", name="gift_detail_partial", response_class=HTMLResponse)
def gift_detail_partial(
    party_id: UUID,
    gift_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
):
    gift = session.get(Gift, gift_id)
    party = session.get(Party, party_id)

    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_detail.html",
        context={"party": party, "gift": gift},
    )


# Regresa el formulario para editar un regalo específico, obtiene el datalle del regalo para prellenar el formulario
@router.get("/{gift_id}/edit", name="gift_update_partial", response_class=HTMLResponse)
def gift_update_partial(
    party_id: UUID,
    gift_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
):
    gift = session.get(Gift, gift_id)

    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found"
        )

    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_update.html",
        context={"gift": gift, "party_id": party_id},
    )


# Actualiza los datos del regalo en la base de datos y regresa el detalle actualizado del regalo
@router.put(
    "/{gift_id}/edit", name="gift_update_save_partial", response_class=HTMLResponse
)
def gift_update_save_partial(
    party_id: UUID,
    gift_id: UUID,
    gift_form: Annotated[GiftForm, Form()],
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
):
    party = session.get(Party, party_id)
    gift = session.get(Gift, gift_id)

    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found"
        )

    gift.gift_name = gift_form.gift_name
    gift.price = gift_form.price
    gift.link = gift_form.link

    session.add(gift)
    session.commit()
    session.refresh(gift)

    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_detail.html",
        context={"gift": gift, "party": party},
    )


@router.delete(
    "/{gift_id}/delete", name="gift_remove_partial", response_class=HTMLResponse
)
def gift_remove_partial(
    gift_id: UUID,
    request: Request,
    templates: Templates,
    session: Session = Depends(get_session),
):
    gift = session.get(Gift, gift_id)

    if not gift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Gift not found"
        )

    session.delete(gift)
    session.commit()

    return templates.TemplateResponse(
        request=request,
        name="gift_registry/partial_gift_removed.html",
        context={"gift": gift},
    )
