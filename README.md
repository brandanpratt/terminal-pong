# 🏓 Terminal Pong

Classic Pong in your terminal. Pure Python + `curses` — no installs, no dependencies.

```
                     P1  3   :   2  CPU (normal)
────────────────────────────────────────────────────────────
                              :
  ▒                                                       ▒
  ▒                           :          O                ▒
  ▒                                                       ▒
  ▒                           :                           ▒
  ▒                                                       ▒
                              :
────────────────────────────────────────────────────────────
```

## Play

```bash
git clone https://github.com/brandanpratt/terminal-pong.git
cd terminal-pong
python3 pong.py
```

Works on macOS and Linux out of the box (Windows: `pip install windows-curses` first).
Minimum terminal size: 40×15 — bigger is better.

## Modes

- **1 Player vs CPU** — easy, normal, or hard
- **2 Players** — same keyboard, couch-co-op style

## Controls

| Key | Action |
|---|---|
| `W` / `S` | Left paddle up / down |
| `↑` / `↓` | Right paddle (2P) — or left paddle vs CPU |
| `P` | Pause |
| `Q` | Quit to menu / exit |
| `R` | Rematch (on the win screen) |

First to **7** wins. The ball speeds up on every hit, and where it hits your paddle sets the bounce angle — edge hits send it flying.

## Tweak it

All the knobs live at the top of `pong.py`: `WIN_SCORE`, `PADDLE_H`, `BALL_START_SPEED`, `BALL_SPEEDUP`, `CPU_SPEED`, etc.

## License

MIT
