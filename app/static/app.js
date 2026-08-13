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
const cluesContainer = document.getElementById("clues");

async function loadToday() {
  const response = await fetch(
    `/api/today?player_id=${encodeURIComponent(playerId)}`,
  );

  if (!response.ok) {
    result.textContent = "Could not load today's game.";
    return;
  }

  const game = await response.json();

  streakValue.textContent = game.streak;
  result.textContent = game.message;

  cluesContainer.innerHTML = "";

  game.clues.forEach((clue) => {
    const clueElement = document.createElement("p");
    clueElement.textContent = clue;
    cluesContainer.appendChild(clueElement);
  });

  if (game.already_played) {
    guessButton.disabled = true;
    guessInput.disabled = true;
  }
}

guessButton.addEventListener("click", async () => {
  const guess = Number(guessInput.value);

  if (!Number.isInteger(guess) || guess < 1 || guess > 100) {
    result.textContent = "Enter a number between 1 and 100.";
    return;
  }

  guessButton.disabled = true;
  guessButton.textContent = "GUESSING...";

  try {
    const response = await fetch("/api/guess", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        player_id: playerId,
        guess: guess,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      result.textContent = data.detail;
      guessButton.disabled = false;
      guessButton.textContent = "GUESS";
      return;
    }

    result.textContent = data.message;
    streakValue.textContent = data.streak;

    // Attempt has been used for today.
    guessButton.textContent = "GUESS";
    guessInput.disabled = true;
  } catch (error) {
    result.textContent = "Could not submit your guess. Please try again.";
    guessButton.disabled = false;
    guessButton.textContent = "GUESS";
  }
});

guessInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    guessButton.click();
  }
});

loadToday();