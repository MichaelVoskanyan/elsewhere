# Worldsim

A terminal-first adventure world sim with a deterministic game engine and a pluggable "dungeon master" director layer.

This prototype is built around one design rule:

- The engine owns rules, rolls, HP, movement, map topology, and state mutation.
- The director owns names, hooks, atmosphere, scene framing, and narrative possibilities.

That keeps the game coherent while still allowing an LLM to improvise.

## What Exists

- Colorized TUI built with `textual`
- Top tabs, bordered panels, and a command bar closer to the reference layout
- Procedural world map with biome coloring
- Named locations and NPCs
- Player creation with archetype selection
- Command loop for moving, exploring, talking, resting, fighting, and waiting
- Living world events that continue between turns
- Local campaign persistence in `data/campaign.json`
- Compact memory entries for locations, NPCs, hooks, battles, and discoveries
- A `MockDirector` that behaves like a local DM
- A `Director` interface where a real LLM backend can be plugged in later

## Run

```bash
python3 -m pip install -r requirements.txt
python3 main.py
```

## Commands

- `north` / `south` / `east` / `west`
- `move north`
- `look`
- `explore`
- `talk`
- `attack`
- `rest`
- `wait`
- `help`
- `quit`

## Architecture

`worldsim/models.py`

- Game state, locations, events, NPCs, and director responses

`worldsim/engine.py`

- World generation
- Command parsing
- Deterministic resolution of movement, combat, rest, and discovery

`worldsim/director.py`

- `Director` base class
- `MockDirector` for local play
- A prompt contract showing how a real LLM should speak to the engine

`worldsim/memory.py`

- Compact long-term memory store
- Local save/load for campaign state
- Retrieval of relevant memories for the director layer

`worldsim/tui.py`

- `textual` app shell, tabs, command bar, and live panel updates

`worldsim/worldsim.tcss`

- Layout and color styling for the terminal UI

`worldsim/game.py`

- Launcher for the `textual` app

## Wiring In A Real LLM

The director should never directly mutate state. It should return structured intent, for example:

```json
{
  "title": "Ruined Shrine",
  "narration": "A broken shrine leans out of the mist.",
  "mechanical_request": "exploration_check",
  "difficulty": 11,
  "tags": ["mystery", "ancient"],
  "follow_up_hook": "Someone still leaves fresh candles here."
}
```

The engine then decides:

- whether a check is needed
- what dice to roll
- whether the player takes damage
- what loot or XP is granted
- how the world state changes

That is the handoff boundary between "LLM as DM" and "code as rules engine."

## Memory Model

The game now keeps two different forms of persistence:

- Exact campaign state in `data/campaign.json`
- Compressed memory entries for important facts, so the director can pull a few relevant reminders instead of replaying the full log

That is the basis for a scalable LLM-backed campaign loop: retrieval first, full transcript never.
