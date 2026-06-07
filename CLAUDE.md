# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the game

No build step. Open directly in a browser:

```bash
open index.html
```

Three.js r160 is loaded from unpkg CDN via an importmap — no npm or bundler involved.

## QA

```bash
pip install playwright
playwright install chromium
python3 qa.py        # headed by default; screenshots → qa_screenshots/
```

## Architecture

The entire game lives in a single file: `index.html`. It contains inline CSS, inline HTML, and a `<script type="module">` block. There is no separate JS or CSS file.

### Key classes (in the script block)

- **`Robot`** (~line 452) — humanoid fighter. Builds a Three.js `Group` of box-geometry limbs. Owns physics state (`x`, `y`, `vx`, `vy`), combat state (`hp`, `isBlocking`, `isDead`), and an animation state machine. `update(opponent, dt, input)` runs physics, AI (when `input` is null), hit detection, and animation each frame.
- **`CentipedeRobot`** (~line 752) — centipede fighter. Same interface as `Robot` but different geometry (segmented body), stats (120 HP), and attack set (bite, leg sweep, tail sting).

### Game loop & state

- `gameLoop(timestamp)` is the single `requestAnimationFrame` loop. It only ticks physics/AI when `roundStarted && !gameOver && p1 && p2`.
- `initGame(selectedP1Type)` instantiates `p1` and `p2`, sets names/colors, and starts the round. Called by `window.startGame(type)` from the character-select onclick.
- `restartGame()` hides the game-over overlay and shows the character-select screen again; it does **not** call `initGame` — that happens when the player picks a fighter.
- Global state: `p1`, `p2`, `p1Type`, `p2Type`, `p1Name`, `p2Name`, `roundTime`, `roundNum`, `gameOver`, `roundStarted`.

### Fighter pairing

| Player picks | CPU fighter |
|---|---|
| IRON-X (humanoid) | GORE-C (centipede, 120 HP) |
| VENOM-C (centipede) | TITAN-9 (humanoid, 100 HP) |

### HUD

`#char-select` is a child of `#hud`. The character-select overlay has `background: #000` (fully opaque) so the HUD elements behind it are hidden during selection. `#hud` is always `display: block`; individual visibility is controlled by the opaque overlay, not by hiding the HUD itself.

### Hit detection

Each fighter's `update()` checks whether the opponent is within range during an active attack frame and calls `opponent.hp = Math.max(0, opponent.hp - actualDmg)`. Damage is reduced when the opponent is blocking.
