const guessInput = document.getElementById("guess-input");
const guessButton = document.getElementById("guess-button");
const streakValue = document.getElementById("streak-value");
const result = document.getElementById("result");

let streak = 0;

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