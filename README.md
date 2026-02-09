# ♟️ Chess Engine with GUI & AI (Python + Pygame)

A fully playable **Chess game with GUI and AI**, built from scratch using **Python**, **Pygame**, and a custom chess engine.  
Supports **Player vs Player** and **Player vs AI**, with legal move validation, timers, SAN move logging, and a threaded AI for smooth gameplay.

This project is designed to be **educational, readable, and extendable**, not a black-box chess library.

---

## ✨ Features

- 🎮 Player vs Player (PvP)
- 🤖 Player vs AI (PvAI)
- ♜ Custom chess engine (no external chess libraries)
- 🧠 Minimax-based AI
- ⏱️ Chess clock (time control)
- 📝 SAN (Standard Algebraic Notation) move log
- 🎨 Graphical UI using Pygame
- ⚡ AI runs in a background thread (no UI freezing)
- 🪟 Windows `.exe` build supported

---

## 📂 Project Structure

chess-engine/
│
├── main.py # Game loop, UI, input handling
├── engine.py # Chess rules & move generation
├── movefinder.py # AI (minimax + evaluation)
│
├── images/ # Piece images
│ ├── wp.png
│ ├── bp.png
│ ├── wK.png
│ └── ...
│
├── README.md
└── requirements.txt


---

## ♞ High-Level Architecture

┌──────────────┐
│   Player /   │
│     AI       │
└──────┬───────┘
       │ move request
       v
┌──────────────┐
│  main.py     │
│  (Game Loop) │
└──────┬───────┘
       │ validate / apply
       v
┌──────────────┐
│ engine.py    │
│ GameState    │
│ Move Rules   │
└──────┬───────┘
       │ board snapshot
       v
┌──────────────┐
│ movefinder.py│
│ Minimax AI   │
└──────────────┘
## ♜ Move Flow

Mouse Click
|
v
Validate Move
|
v
engine.makeMove()
|
v
Update Board & SAN
|
v
Switch Turn
|
v
AI Thread (if PvAI)


---

## 🤖 AI Details

- Uses **Minimax search** with fixed depth
- Material-based evaluation
- Runs in a **separate thread** to avoid freezing the UI
- Designed for **casual play**, not competitive engines

---

## ⏱️ Time Control

- Default: **10 minutes per side**
- Time decreases **only during the active player’s turn**
- Game ends by:
  - Checkmate
  - Stalemate
  - Timeout

---

## ⚠️ Known Limitations

This project intentionally keeps complexity manageable.

- ❌ No opening book (AI does not know theory)
- ❌ No transposition table
- ❌ Fixed AI depth
- ❌ No draw by repetition or 50-move rule
- ❌ AI evaluation is mostly material-based
- ❌ Not optimized for competitive engine strength

These are **design decisions**, not bugs.

---

## ▶️ Running from Source

### Requirements

- Python **3.10+**
- Pygame CE

```bash
pip install pygame-ce
python main.py

