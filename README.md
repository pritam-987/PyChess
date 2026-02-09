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

<img width="381" height="666" alt="image" src="https://github.com/user-attachments/assets/70d4a195-ad40-49fa-871b-5b60ec82fcb5" />


---

## ♞ High-Level Architecture

<img width="388" height="592" alt="image" src="https://github.com/user-attachments/assets/60624c30-090d-41cc-92f4-08f7bd037af4" />

## ♜ Move Flow
<img width="196" height="236" alt="image" src="https://github.com/user-attachments/assets/08a1109e-a89b-4020-bde9-bebb69a42cf2" />



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



