# Distribution Package Structure

This document describes what files should be included when distributing the game to users.

## Files to Include for Distribution

### Core Framework (Required)
```
core/
├── __init__.py
├── base_manager.py          # Abstract game manager base class
├── base_player.py            # Helper functions for player scripts
└── local_player_container.py # Local subprocess execution (no Docker)
```

### Game: Tic-Tac-Toe
```
games/tictactoe/
├── __init__.py
├── tictactoe_manager.py      # Game engine (disclosed)
├── tictactoe_player.py       # Example player: first empty cell strategy
└── tictactoe_player_blocking.py  # Example player: blocking strategy
```

### Game: Prisoner's Dilemma
```
games/prisoners_dilemma/
├── __init__.py
├── pd_manager.py             # Game engine (disclosed)
├── pd_player_always_cooperate.py # Example player: always cooperate
└── pd_player_tit_for_tat.py      # Example player: tit-for-tat
```

### Runner Scripts
```
run_tictactoe.py             # Run tic-tac-toe game
run_prisoners_dilemma.py     # Run prisoner's dilemma game
```

### Documentation
```
README.md                    # Complete documentation
```

## Files NOT to Include (Internal/Development Only)

```
core/player_container.py     # Docker-based execution (internal only)
manager.py                   # Legacy manager (reference only)
player.py                    # Legacy player (reference only)
.git/                        # Git repository
.venv/                       # Virtual environment
__pycache__/                 # Python cache
*.pyc                        # Compiled Python files
```

## Creating Distribution Package

To create a distribution package:

```bash
# Create distribution directory
mkdir -p game_arena_dist

# Copy core files
cp -r core game_arena_dist/
rm -f game_arena_dist/core/player_container.py  # Remove Docker version

# Copy games
cp -r games game_arena_dist/

# Copy runners
cp run_tictactoe.py run_prisoners_dilemma.py game_arena_dist/

# Copy documentation
cp README.md game_arena_dist/

# Create archive
tar -czf game_arena.tar.gz game_arena_dist/
```

## User Installation

Users simply need:
1. Python 3.8+
2. Extract the archive
3. Run games with: `python run_tictactoe.py <player1> <player2>`

No Docker required!
