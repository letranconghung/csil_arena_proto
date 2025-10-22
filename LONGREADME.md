# Game Arena: Multi-Player Strategy Games

A framework for running competitive strategy games between AI players. Players run in isolated environments and communicate via stdin/stdout with a central game manager.

## Features

- **Generic Architecture**: Separation of game logic from communication protocol
- **Two Game Types**: Turn-based (Tic-Tac-Toe) and simultaneous (Prisoner's Dilemma)
- **Minimal Communication**: Manager sends only opponent's last move + time index
- **Easy Player Development**: Import helper functions from `base_player`
- **Debug Logging**: Players can output debug messages to stderr
- **Timeout Enforcement**: Configurable timeouts prevent hung players
- **No Docker Required**: Runs as local Python subprocesses

## Quick Start

### Installation

Requires Python 3.8 or higher. No additional dependencies needed.

```bash
# Run a tic-tac-toe game
python run_tictactoe.py games/tictactoe/tictactoe_player.py games/tictactoe/tictactoe_player_blocking.py

# Run a prisoner's dilemma game
python run_pd.py games/pd/pd_player_always_cooperate.py games/pd/pd_player_tit_for_tat.py
```

## Writing Your Own Player

### Player Script Structure

All player scripts follow this basic structure:

```python
#!/usr/bin/env python3
import sys
import os

# Import base_player helpers
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../core'))
from base_player import debug, send_message, player_main_loop

# Your game state
my_state = {}

def handle_message(message):
    """Handle messages from manager. Return False to exit."""
    msg_type = message.get("type")

    if msg_type == "game_start":
        # Initialize your strategy
        debug("Game starting!")
        return True

    elif msg_type == "your_turn":
        # Make your move
        my_move = decide_move(message)
        send_message({"move": my_move})
        return True

    elif msg_type == "game_over":
        # Game finished
        return False

    return True

if __name__ == "__main__":
    player_main_loop(handle_message)
```

### Base Player Functions

- **`debug(message)`**: Log debug info to stderr (visible in game output)
- **`send_message(dict)`**: Send JSON message to manager via stdout
- **`player_main_loop(handler_func)`**: Main event loop that calls your handler

## Game 1: Tic-Tac-Toe

Turn-based game where players alternate placing X or O on a 3x3 board.

### Protocol

**Game Start:**
```json
{"type": "game_start", "symbol": "X", "game": "tictactoe"}
```

**Your Turn:**
```json
{
  "type": "your_turn",
  "time_index": 2,
  "opponent_move": {"position": 4, "symbol": "O"}  // null on first turn
}
```

**Your Response:**
```json
{"move": 0}  // Position 0-8 on the board
```

**Game Over:**
```json
{
  "type": "game_over",
  "result": "X wins",
  "winner": "X",
  "board": ["X", "X", "X", "O", "O", "", "", "", ""]
}
```

### Board Layout

```
 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8
```

### Example Players

- **tictactoe_player.py**: Picks first empty cell
- **tictactoe_player_blocking.py**: Prefers center, blocks winning moves, aims for corners

### Writing a Tic-Tac-Toe Player

```python
# Track board state locally
board = [""] * 9

def handle_message(message):
    global board

    if message["type"] == "your_turn":
        # Update board with opponent's move
        if message.get("opponent_move"):
            pos = message["opponent_move"]["position"]
            symbol = message["opponent_move"]["symbol"]
            board[pos] = symbol

        # Your strategy here
        my_move = find_best_move(board)
        board[my_move] = "X"  # Update your own board

        send_message({"move": my_move})
    return True
```

## Game 2: Prisoner's Dilemma

Simultaneous 30-round game where both players choose to cooperate (C) or defect (D) each round.

### Payoff Matrix

| You \\ Opponent | Cooperate | Defect |
|-----------------|-----------|--------|
| **Cooperate**   | 3 / 3     | 0 / 5  |
| **Defect**      | 5 / 0     | 1 / 1  |

### Protocol

**Game Start:**
```json
{
  "type": "game_start",
  "game": "prisoners_dilemma",
  "rounds": 30,
  "rules": { /* payoff matrix */ }
}
```

**Your Turn:**
```json
{
  "type": "your_turn",
  "round": 5,
  "your_score": 12,
  "last_round": {
    "your_move": "C",
    "opponent_move": "D",
    "your_score_gained": 0
  }
}
```

**Your Response:**
```json
{"move": "C"}  // "C" for cooperate, "D" for defect
```

**Game Over:**
```json
{
  "type": "game_over",
  "result": "Draw with 90 points each",
  "winner": null,
  "final_scores": {"player1": 90, "player2": 90}
}
```

### Example Players

- **pd_player_always_cooperate.py**: Always cooperates
- **pd_player_tit_for_tat.py**: Cooperates first, then copies opponent's last move

### Writing a Prisoner's Dilemma Player

```python
def handle_message(message):
    if message["type"] == "your_turn":
        last_round = message.get("last_round")

        if last_round:
            # React to opponent's last move
            opponent_move = last_round["opponent_move"]
            my_move = your_strategy(opponent_move)
        else:
            # First round
            my_move = "C"

        send_message({"move": my_move})
    return True
```

## Architecture

### For Distributors

The framework consists of:

1. **Core** (`core/`): Base classes and player container
   - `base_manager.py`: Abstract game manager
   - `base_player.py`: Helper functions for players
   - `local_player_container.py`: Subprocess management

2. **Games** (`games/<game_name>/`): Game-specific implementations
   - `*_manager.py`: Game engine (disclosed to users)
   - `*_player.py`: Example player implementations

3. **Runners** (`run_*.py`): Entry points to start games

### Internal vs Distributed Files

**Include in distribution:**
- All files in `core/` (except `player_container.py` - Docker version)
- All files in `games/`
- All `run_*.py` files
- This README

**Exclude from distribution:**
- `core/player_container.py` (Docker-based, for internal use)
- `.git/`, `.venv/`, `__pycache__/`

See [DISTRIBUTION.md](DISTRIBUTION.md) for detailed packaging instructions.


## Tips for Writing Players

1. **Maintain Local State**: Track game state in your script, don't rely on manager
2. **Use Debug Logging**: `debug()` messages help you understand what your player is doing
3. **Handle All Message Types**: Especially `game_start`, `your_turn`, and `game_over`
4. **Validate Inputs**: Check that opponent moves make sense before trusting them
5. **Test Locally**: Run against example players before submitting
6. **Stay Within Timeout**: Players must respond within 10 seconds (default)

## Advanced: Creating New Games

To add a new game:

1. Create `games/mygame/mygame_manager.py` extending `GameManager`
2. Implement all abstract methods (see `base_manager.py`)
3. Create example player scripts
4. Create `run_mygame.py` following existing patterns

Key methods to implement:
- `should_request_moves_simultaneously()`: Turn-based or simultaneous?
- `get_next_player_ids()`: Who moves next?
- `get_move_request_message()`: What info to send players?
- `validate_move()` and `apply_move()`: Process player moves
- `is_game_over()` and `get_game_result()`: End conditions

## License

[Your License Here]

## Contributing

[Your contribution guidelines]
