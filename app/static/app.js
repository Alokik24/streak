const PLAYER_ID_KEY = "streak_player_id";

function getPlayerId() {
    let playerId = localStorage.getItem(PLAYER_ID_KEY);

    if (!playerId) {
        playerId = crypto.randomUUID();
        localStorage.setItem(PLAYER_ID_KEY, playerId);
    }

    return playerId;
}

const playerId = getPlayerId();

const guessInput = document.getElementById("guess-input");
const guessButton = document.getElementById("guess-button");
const streakValue = document.getElementById("streak-value");
const result = document.getElementById("result");


async function loadToday() {
    const response = await fetch(
        `/api/today?player_id=${encodeURIComponent(playerId)}`
    );

    if (!response.ok) {
        result.textContent = "Could not load today's game.";
        return;
    }

    const game = await response.json();

    streakValue.textContent = game.streak;

    if (game.already_played) {
        result.textContent = "You already played today.";
        guessButton.disabled = true;
    }
}


guessButton.addEventListener("click", async () => {
    const guess = Number(guessInput.value);

    if (!Number.isInteger(guess) || guess < 1 || guess > 100) {
        result.textContent = "Enter a number between 1 and 100.";
        return;
    }

    guessButton.disabled = true;

    try {
        const response = await fetch("/api/guess", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                player_id: playerId,
                guess: guess
            })
        });

        const data = await response.json();

        if (!response.ok) {
            result.textContent = data.detail;
            return;
        }

        result.textContent = data.message;
        streakValue.textContent = data.streak;

    } catch (error) {
        result.textContent = "Something went wrong.";
    }
});

guessInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        guessButton.click();
    }
});


loadToday();