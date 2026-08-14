from datetime import date, timedelta
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
from app.game import get_today_answer, get_today_clues


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

    player_id = player[0]
    current_streak = player[1]
    last_played_date = player[2]
    last_puzzle_date = player[3]

    today = date.today()
    today_string = today.isoformat()

    missed_day = False
    
    # Detect a missed day and immediately break the old streak.
    if last_played_date is not None:
        last_played = date.fromisoformat(last_played_date)
        yesterday = today - timedelta(days=1)

        if last_played < yesterday:
            missed_day = True
            current_streak = 0

            update_player(
                player_id=player_id,
                streak=0,
                last_played_date=last_played_date,
                last_puzzle_date=last_puzzle_date,
            )

    already_played = last_played_date == today_string

    if already_played:
        message = "You already played today."
    elif missed_day:
        message = "You missed a day. Your previous streak was broken."
    else:
        message = "Make your guess."

    return {
        "min": 1,
        "max": 100,
        "clues": get_today_clues(today),
        "streak": current_streak,
        "already_played": already_played,
        "message": message,
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

    # One guess per day.
    if last_played_date == today_string:
        raise HTTPException(
            status_code=409,
            detail="You have already played today.",
        )

    # If the player missed one or more days, the old streak
    # is already considered broken.
    if last_played_date is not None:
        last_played = date.fromisoformat(last_played_date)
        yesterday = today - timedelta(days=1)

        if last_played < yesterday:
            current_streak = 0

    answer = get_today_answer(today)
    correct = request.guess == answer

    if not correct:
        new_streak = 0
        result = "incorrect"
        message = "Wrong guess. Your streak was reset."

    else:
        # First successful day or successful guess after
        # a missed day starts a new streak.
        if last_played_date is None:
            new_streak = 1
            message = "Correct! You started a new streak."

        else:
            last_played = date.fromisoformat(last_played_date)
            yesterday = today - timedelta(days=1)

            if last_played == yesterday:
                new_streak = current_streak + 1
                message = "Correct! Your streak continues."

            else:
                new_streak = 1
                message = "Correct! You started a new streak."

        result = "correct"

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