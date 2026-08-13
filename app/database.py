import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "streak.db"


def get_connection():
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

    player = connection.execute(
        """
        SELECT player_id, streak, last_played_date, last_puzzle_date
        FROM player
        WHERE player_id = ?
        """,
        (player_id,),
    ).fetchone()

    if player is None:
        connection.execute(
            """
            INSERT INTO player (
                player_id,
                streak,
                last_played_date,
                last_puzzle_date
            )
            VALUES (?, 0, NULL, NULL)
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