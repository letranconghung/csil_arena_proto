#!/usr/bin/env python3
"""
Tic-tac-toe player with blocking strategy.
- Prefers center if available
- Otherwise blocks opponent's winning move if detected
- Otherwise picks first empty cell
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


class BlockingTicTacToePlayer(BasePlayer):
    """
    Tic-tac-toe player with blocking strategy.
    Maintains board state and uses strategic decision making.
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
        debug(f"Game starting! I am player '{self.my_symbol}' (blocking strategy)")

    def check_winning_move(self, symbol):
        """
        Check if there's a winning move for the given symbol.
        Returns the position of the winning move, or None.
        """
        # Winning combinations
        wins = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]

        for combo in wins:
            values = [self.board[i] for i in combo]
            # Check if two are the symbol and one is empty
            if values.count(symbol) == 2 and values.count("") == 1:
                # Return the empty position
                for i in combo:
                    if self.board[i] == "":
                        return i
        return None

    def choose_move(self):
        """Choose the best move using blocking strategy."""
        # 1. Prefer center if available
        if self.board[4] == "":
            debug("Choosing center")
            return 4

        # 2. Check if we can win
        winning_move = self.check_winning_move(self.my_symbol)
        if winning_move is not None:
            debug(f"Found winning move: {winning_move}")
            return winning_move

        # 3. Block opponent's winning move
        blocking_move = self.check_winning_move(self.opponent_symbol)
        if blocking_move is not None:
            debug(f"Blocking opponent at: {blocking_move}")
            return blocking_move

        # 4. Prefer corners
        corners = [0, 2, 6, 8]
        for corner in corners:
            if self.board[corner] == "":
                debug(f"Choosing corner: {corner}")
                return corner

        # 5. Take any available space
        for i, cell in enumerate(self.board):
            if cell == "":
                debug(f"Choosing first available: {i}")
                return i

        return None

    def on_your_turn(self, message):
        """
        Make a move using blocking strategy.
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

        # Use blocking strategy
        move = self.choose_move()

        if move is not None:
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
    player_main_loop(BlockingTicTacToePlayer)
