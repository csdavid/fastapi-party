from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from party_app.routes.main import api_router


app = FastAPI()

app.include_router(api_router)

app.mount(
    "/party_app/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)


@app.get("/")
async def root():
    return {"message": "Welcome to the Party App!"}
