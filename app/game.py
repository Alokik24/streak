import hashlib
from datetime import date


def get_today_answer(game_date: date | None = None) -> int:
    if game_date is None:
        game_date = date.today()

    value = hashlib.sha256(
        f"streak-secret-{game_date.isoformat()}".encode()
    ).hexdigest()

    answer = int(value, 16) % 100 + 1

    # Guarantee that tomorrow cannot have the same answer.
    tomorrow = game_date.fromordinal(game_date.toordinal() + 1)

    tomorrow_value = hashlib.sha256(
        f"streak-secret-{tomorrow.isoformat()}".encode()
    ).hexdigest()

    tomorrow_answer = int(tomorrow_value, 16) % 100 + 1

    if tomorrow_answer == answer:
        answer = answer % 100 + 1

    return answer

# if __name__ == "__main__":
#     from datetime import date

#     print(get_today_answer(date.today()))