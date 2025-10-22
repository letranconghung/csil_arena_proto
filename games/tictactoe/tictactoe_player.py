#!/usr/bin/env python3
"""
Simple tic-tac-toe player that picks the first empty cell.
"""
import sys
import os

# Add core directory to path for local execution
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../core'))

try:
    from base_player import BasePlayer, debug, player_main_loop
except ImportError:
    # Fallback for when running in Docker with base_player.py mounted
    import base_player
    BasePlayer = base_player.BasePlayer
    debug = base_player.debug
    player_main_loop = base_player.player_main_loop


class SimpleTicTacToePlayer(BasePlayer):
    """
    Simple tic-tac-toe player that picks the first empty cell.
    Maintains board state internally.
    """

    def __init__(self):
        super().__init__()
        self.board = [""] * 9
        self.my_symbol = None
        self.opponent_symbol = None
        self.move_history = []  # Track all moves made

    def on_game_start(self, message):
        """Initialize game state when game starts."""
        self.my_symbol = message.get("symbol")
        self.opponent_symbol = "O" if self.my_symbol == "X" else "X"
        debug(f"Game starting! I am player '{self.my_symbol}'")

    def on_your_turn(self, message):
        """
        Make a move by selecting the first empty cell.
        Returns the position (0-8) to play.
        """
        time_index = message.get("time_index")
        opponent_move = message.get("opponent_move")

        # Update board with opponent's move if present
        if opponent_move is not None:
            pos = opponent_move["position"]
            symbol = opponent_move["symbol"]
            self.board[pos] = symbol
            debug(f"Opponent played {symbol} at position {pos}")

        debug(f"Time index: {time_index}, Board: {self.board}")

        # Simple AI: find first empty cell
        move = None
        for i, cell in enumerate(self.board):
            if cell == "":
                move = i
                break

        if move is not None:
            debug(f"Choosing move: {move}")
            # Update local board state
            self.board[move] = self.my_symbol
            self.move_history.append(move)
            return move
        else:
            debug("No valid moves available")
            return -1

    def on_game_over(self, message):
        """Called when game ends."""
        result = message.get("result")
        winner = message.get("winner")
        debug(f"Game over! Result: {result}, Winner: {winner}")
        debug(f"My moves: {self.move_history}")
        debug(f"Final board: {self.board}")


if __name__ == "__main__":
    player_main_loop(SimpleTicTacToePlayer)
