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


guessButton.addEventListener("click", () => {
    const guess = Number(guessInput.value);

    if (!Number.isInteger(guess) || guess < 1 || guess > 100) {
        result.textContent = "Enter a number between 1 and 100.";
        return;
    }

    result.textContent = `You guessed ${guess}.`;
});


guessInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        guessButton.click();
    }
});


loadToday();