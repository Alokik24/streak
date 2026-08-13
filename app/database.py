import os
import sqlite3
from pathlib import Path

import psycopg
from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "streak.db"

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    if DATABASE_URL:
        return psycopg.connect(DATABASE_URL)

    return sqlite3.connect(DATABASE_PATH)


def create_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS player (
            player_id TEXT PRIMARY KEY,
            streak INTEGER NOT NULL DEFAULT 0,
            last_played_date TEXT,
            last_puzzle_date TEXT
        )
        """
    )

    connection.commit()
    connection.close()


def get_or_create_player(player_id):
    connection = get_connection()

    placeholder = "%s" if DATABASE_URL else "?"

    player = connection.execute(
        f"""
        SELECT player_id, streak, last_played_date, last_puzzle_date
        FROM player
        WHERE player_id = {placeholder}
        """,
        (player_id,),
    ).fetchone()

    if player is None:
        connection.execute(
            f"""
            INSERT INTO player (
                player_id,
                streak,
                last_played_date,
                last_puzzle_date
            )
            VALUES ({placeholder}, 0, NULL, NULL)
            """,
            (player_id,),
        )

        connection.commit()

        player = (
            player_id,
            0,
            None,
            None,
        )

    connection.close()

    return player


def update_player(
    player_id,
    streak,
    last_played_date,
    last_puzzle_date,
):
    connection = get_connection()

    placeholder = "%s" if DATABASE_URL else "?"

    connection.execute(
        f"""
        UPDATE player
        SET
            streak = {placeholder},
            last_played_date = {placeholder},
            last_puzzle_date = {placeholder}
        WHERE player_id = {placeholder}
        """,
        (
            streak,
            last_played_date,
            last_puzzle_date,
            player_id,
        ),
    )

    connection.commit()
    connection.close()