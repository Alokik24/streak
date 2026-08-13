from datetime import date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.database import (
    create_database,
    get_or_create_player,
    update_player,
)
from app.game import get_today_answer


app = FastAPI()

create_database()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class GuessRequest(BaseModel):
    player_id: str
    guess: int


@app.get("/")
def serve_frontend():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/today")
def get_today(player_id: str = Query(default="local-player")):
    player = get_or_create_player(player_id)

    last_played_date = player[2]
    already_played = last_played_date == date.today().isoformat()

    return {
        "min": 1,
        "max": 100,
        "streak": player[1],
        "already_played": already_played,
    }


@app.post("/api/guess")
def submit_guess(request: GuessRequest):
    today = date.today()
    today_string = today.isoformat()

    if request.guess < 1 or request.guess > 100:
        raise HTTPException(
            status_code=400,
            detail="Guess must be between 1 and 100.",
        )

    player = get_or_create_player(request.player_id)

    player_id = player[0]
    current_streak = player[1]
    last_played_date = player[2]

    if last_played_date == today_string:
        raise HTTPException(
            status_code=409,
            detail="You have already played today.",
        )

    answer = get_today_answer(today)

    correct = request.guess == answer

    if correct:
        new_streak = current_streak + 1
        result = "correct"
        message = "Correct!"
    else:
        new_streak = 0
        result = "incorrect"
        message = "Incorrect."

    update_player(
        player_id=player_id,
        streak=new_streak,
        last_played_date=today_string,
        last_puzzle_date=today_string,
    )

    return {
        "result": result,
        "message": message,
        "streak": new_streak,
    }