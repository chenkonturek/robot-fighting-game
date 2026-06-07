# Robot Fighting Game

A 3D robot fighting game built with [Three.js](https://threejs.org/). No build step — open `index.html` in any modern browser and play.

![Game screenshot](https://github.com/chenkonturek/robot-fighting-game/raw/main/preview.png)

## Fighters

| Fighter | Role | Type | HP | Style |
|---|---|---|---|---|
| **IRON-X** | Player | Humanoid | 100 | Balanced — punch, kick, uppercut |
| **VENOM-C** | Player | Centipede | 120 | Aggressive — venom bite, leg sweep, tail sting |
| **GORE-C** | CPU | Centipede | 120 | AI opponent when you play as IRON-X |
| **TITAN-9** | CPU | Humanoid | 100 | AI opponent when you play as VENOM-C |

At the character select screen, pick who **you** want to play. The CPU always controls the opposing fighter.

## Controls

| Key | Action |
|---|---|
| `A` / `D` | Move left / right |
| `W` | Jump |
| `J` | Punch / Bite |
| `K` | Kick / Leg sweep |
| `U` | Uppercut / Tail sting |
| `L` / `Shift` | Block |

Arrow keys also work for movement.

## How to play

```bash
# Clone and open — no install needed
git clone https://github.com/chenkonturek/robot-fighting-game.git
cd robot-fighting-game
open index.html
```

Or just download `index.html` and open it directly.

## Features

- 3D arena with neon lighting, grid floor, and audience silhouettes
- Two fully articulated robots with per-bone animations
- Walk cycle, attack, block, hurt, jump, and death animations
- Spark particle effects on hits with screen flash
- Dynamic camera that follows the action and zooms with distance
- AI opponent with approach / retreat / attack / block state machine
- Health bars that shift color as HP drops
- 99-second round timer with KO and time-out win conditions

## QA

A Playwright script covers the main game flows:

```bash
pip install playwright
playwright install chromium
python3 qa.py
```

Runs in a headed browser by default so you can watch the test execute. Screenshots are saved to `qa_screenshots/`.

## Tech

- [Three.js](https://threejs.org/) r160 — loaded from CDN via import map
- Vanilla JS ES modules, no framework or build tooling
- [Playwright](https://playwright.dev/) for browser-based QA
