import hashlib
from datetime import date
import itertools

def get_today_answer(game_date: date | None = None) -> int:
    if game_date is None:
        game_date = date.today()

    value = hashlib.sha256(
        f"streak-secret-{game_date.isoformat()}".encode()
    ).hexdigest()

    return int(value, 16) % 100 + 1


def get_today_clues(game_date: date | None = None) -> list[str]:
    answer = get_today_answer(game_date)
    numbers = list(range(1, 101))

    clues = []

    # Range clue
    range_start = ((answer - 1) // 10) * 10 - 4
    range_end = range_start + 19

    if range_start < 1:
        range_start = 1
        range_end = 20

    if range_end > 100:
        range_end = 100
        range_start = 81

    clues.append(
        (
            f"The number is between {range_start} and {range_end}. (Both inclusive)",
            lambda n, lo=range_start, hi=range_end: lo <= n <= hi,
        )
    )

    # Parity clue
    if answer % 2 == 0:
        clues.append(
            ("The number is not odd.", lambda n: n % 2 == 0)
        )
    else:
        clues.append(
            ("The number is not even.", lambda n: n % 2 == 1)
        )

    # Divisibility clues
    for divisor in [3, 4, 5, 6, 7, 8, 9, 10]:
        if answer % divisor == 0:
            clues.append(
                (
                    f"The number is divisible by {divisor}.",
                    lambda n, d=divisor: n % d == 0,
                )
            )

    # Digit-sum clue
    digit_sum = sum(int(digit) for digit in str(answer))

    clues.append(
        (
            f"The digits add up to {digit_sum}.",
            lambda n, total=digit_sum: sum(int(d) for d in str(n)) == total,
        )
    )
    
    # Perfect-square clue
    if int(answer ** 0.5) ** 2 == answer:
        clues.append(
            (
                "The number is a perfect square.",
                lambda n: int(n ** 0.5) ** 2 == n,
            )
        )

    # Find exactly three clues that uniquely identify the answer.
    for combination in itertools.combinations(clues, 3):
        matching_numbers = [
            number
            for number in numbers
            if all(condition(number) for _, condition in combination)
        ]

        if matching_numbers == [answer]:
            return [text for text, _ in combination]

    raise RuntimeError("Could not generate a unique three-clue puzzle.")

# if __name__ == "__main__":
#     from datetime import date

#     print(get_today_answer(date.today()))