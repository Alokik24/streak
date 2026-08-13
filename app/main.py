from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.database import create_database, get_or_create_player
from app.game import get_today_answer

app = FastAPI()
create_database()


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/today")
def get_today(player_id: str = Query(default="local-player")):
    player = get_or_create_player(player_id)

    today = __import__("datetime").date.today()
    last_played_date = player[2]

    already_played = last_played_date == today.isoformat()

    return {
        "min": 1,
        "max": 100,
        "streak": player[1],
        "already_played": already_played,
    }