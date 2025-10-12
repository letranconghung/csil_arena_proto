#!/usr/bin/env python3
"""
Tic-Tac-Toe game manager implementation.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.base_manager import GameManager
from typing import Dict, Any, List, Tuple, Optional


class TicTacToeManager(GameManager):
    """Manager for a tic-tac-toe game between two players."""

    def __init__(self):
        super().__init__()
        self.board = [""] * 9
        self.current_symbol = "X"
        self.player_symbols = {}  # player_id -> symbol
        self.move_count = 0
        self.last_move = None
        self.winner = None
        self.result_message = None

    def initialize_game(self) -> None:
        """Initialize the tic-tac-toe game state."""
        self.board = [""] * 9
        self.current_symbol = "X"
        self.move_count = 0
        self.last_move = None
        self.winner = None
        self.result_message = None

        # Assign symbols to players (assuming 2 players with IDs "player1" and "player2")
        player_ids = list(self.players.keys())
        if len(player_ids) != 2:
            raise ValueError("Tic-Tac-Toe requires exactly 2 players")

        self.player_symbols[player_ids[0]] = "X"
        self.player_symbols[player_ids[1]] = "O"

    def get_initial_message(self, player_id: str) -> Dict[str, Any]:
        """Get the initial game_start message for a player."""
        return {
            "type": "game_start",
            "symbol": self.player_symbols[player_id],
            "game": "tictactoe"
        }

    def should_request_moves_simultaneously(self) -> bool:
        """Tic-Tac-Toe is turn-based."""
        return False

    def get_next_player_ids(self) -> List[str]:
        """Get the player ID whose turn it is."""
        # Find the player with the current symbol
        for player_id, symbol in self.player_symbols.items():
            if symbol == self.current_symbol:
                return [player_id]
        return []

    def get_move_request_message(self, player_id: str) -> Dict[str, Any]:
        """Create the move request message for a player."""
        message = {
            "type": "your_turn",
            "time_index": self.move_count
        }

        # Include opponent's last move if available
        if self.last_move is not None:
            opponent_symbol = "O" if self.player_symbols[player_id] == "X" else "X"
            message["opponent_move"] = {
                "position": self.last_move,
                "symbol": opponent_symbol
            }

        return message

    def validate_move(self, player_id: str, move_data: Any) -> Tuple[bool, Optional[str]]:
        """Validate a move from a player."""
        if not isinstance(move_data, int):
            return False, f"Move must be an integer, got {type(move_data)}"

        if move_data < 0 or move_data >= 9:
            return False, f"Move must be between 0 and 8, got {move_data}"

        if self.board[move_data] != "":
            return False, f"Position {move_data} is already occupied"

        # Check it's the player's turn
        if self.player_symbols[player_id] != self.current_symbol:
            return False, "It's not your turn"

        return True, None

    def apply_move(self, player_id: str, move_data: Any) -> None:
        """Apply a validated move to the game state."""
        symbol = self.player_symbols[player_id]
        self.board[move_data] = symbol
        self.last_move = move_data
        self.move_count += 1

        # Check for winner
        self.winner = self._check_winner()
        if self.winner:
            if self.winner == "draw":
                self.result_message = "Draw"
            else:
                self.result_message = f"{self.winner} wins"
        else:
            # Switch players
            self.current_symbol = "O" if self.current_symbol == "X" else "X"

    def is_game_over(self) -> bool:
        """Check if the game has ended."""
        return self.winner is not None

    def get_game_result(self) -> Dict[str, Any]:
        """Get the final result of the game."""
        return {
            "result": self.result_message,
            "winner": self.winner if self.winner != "draw" else None,
            "board": self.board
        }

    def get_display_state(self) -> str:
        """Get a human-readable representation of the board."""
        def cell(i):
            return self.board[i] if self.board[i] else str(i)

        return f"""
  {cell(0)} | {cell(1)} | {cell(2)}
 -----------
  {cell(3)} | {cell(4)} | {cell(5)}
 -----------
  {cell(6)} | {cell(7)} | {cell(8)}
"""

    def _check_winner(self) -> Optional[str]:
        """Check if there's a winner. Returns 'X', 'O', 'draw', or None."""
        # Winning combinations
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]

        for combo in wins:
            if (self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]] and
                self.board[combo[0]] != ""):
                return self.board[combo[0]]

        # Check for draw
        if "" not in self.board:
            return "draw"

        return None
