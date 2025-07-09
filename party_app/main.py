from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount(
    "/party_app/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)
