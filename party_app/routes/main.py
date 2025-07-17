from fastapi import APIRouter

from party_app.routes import party_list, party_detail, new_party

api_router = APIRouter()

api_router.include_router(party_list.router)
api_router.include_router(party_detail.router)
api_router.include_router(new_party.router)
