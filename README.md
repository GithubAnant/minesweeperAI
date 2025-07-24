🧠 Minesweeper AI
A simple AI that plays Minesweeper using logical inference and probability. Built for fun and experimentation with basic constraint satisfaction and game strategy.

⚙️ Features
Plays standard Minesweeper grid

Uses basic logic to flag mines and uncover safe cells

Falls back to probability when unsure

Configurable board size and mine count

🛠️ How It Works
Parses the board state.

Applies deterministic rules (e.g., 1 revealed next to 1 covered = that one is a mine).

If no moves are certain, calculates probabilities and picks the safest move.