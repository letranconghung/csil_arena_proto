#!/usr/bin/env python3
"""
TEMPLATE: Tic-Tac-Toe Player

This is a template for creating your own Tic-Tac-Toe player.
Replace the TODO sections with your strategy implementation.

GAME RULES:
- Standard 3x3 tic-tac-toe
- Players alternate turns placing X or O
- Board positions are numbered 0-8:
    0 | 1 | 2
   -----------
    3 | 4 | 5
   -----------
    6 | 7 | 8
- Win by getting 3 in a row (horizontal, vertical, or diagonal)
"""
import sys
import os

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../core'))

from base_player import BasePlayer, debug, player_main_loop


class MyTicTacToePlayer(BasePlayer):
    """
    TODO: Give your player class a descriptive name and document your strategy here.

    Example strategies you could implement:
    - Pick first available cell
    - Prefer center, then corners, then edges
    - Block opponent's winning moves
    - Try to win if possible
    - Minimax algorithm (optimal play)
    """

    def __init__(self):
        """
        Initialize your player.

        TODO: Add any instance variables you need to track state.

        Examples:
        - self.board = [""] * 9      # Track current board state
        - self.my_symbol = None      # "X" or "O"
        - self.opponent_symbol = None
        - self.move_count = 0        # How many moves have been made
        """
        super().__init__()
        # TODO: Initialize your state variables here
        self.board = [""] * 9  # Basic board tracking (replace with your own if needed)
        self.my_symbol = None

    def on_game_start(self, message):
        """
        Called once at the start of the game.

        INPUT (message dict):
        {
            "type": "game_start",
            "game": "tictactoe",
            "symbol": "X"  # or "O" - your symbol for this game
        }

        TODO: Use this to initialize any strategy-specific state.
        """
        self.my_symbol = message.get("symbol")
        debug(f"Game starting! I am player '{self.my_symbol}'")

    def on_your_turn(self, message):
        """
        Called each turn to get your move.

        INPUT (message dict):
        First turn (if you're X):
        {
            "type": "your_turn",
            "time_index": 0,
            "opponent_move": None
        }

        Later turns:
        {
            "type": "your_turn",
            "time_index": 3,
            "opponent_move": {
                "position": 4,    # They played position 4 (center)
                "symbol": "O"
            }
        }

        OUTPUT: Return an integer 0-8 representing the position to play.
        - Return -1 if no valid move (shouldn't happen in normal play)

        TODO: Implement your strategy here.
        """
        # TODO: Implement your decision logic here

        # Example: Access information from the message
        time_index = message.get("time_index")
        opponent_move = message.get("opponent_move")

        # Update board with opponent's move if present
        if opponent_move is not None:
            pos = opponent_move["position"]
            symbol = opponent_move["symbol"]
            self.board[pos] = symbol
            debug(f"Opponent played {symbol} at position {pos}")

        debug(f"Time index: {time_index}, Board: {self.board}")

        # TODO: Choose your move based on your strategy
        # Example: Simple strategy - pick first empty cell
        my_move = None
        for i, cell in enumerate(self.board):
            if cell == "":
                my_move = i
                break

        if my_move is not None:
            self.board[my_move] = self.my_symbol  # Update our board
            debug(f"Choosing move: {my_move}")
            return my_move
        else:
            debug("No valid moves available!")
            return -1

    def on_game_over(self, message):
        """
        Called once when the game ends.

        INPUT (message dict):
        {
            "type": "game_over",
            "result": "X wins",  # or "O wins" or "Draw"
            "winner": "player1",  # or "player2" or None for draw
            "board": ["X", "O", "X", "O", "X", "O", "X", "", ""]
        }

        TODO: Optional - add any cleanup or final analysis here.
        """
        result = message.get("result")
        winner = message.get("winner")
        debug(f"Game over! Result: {result}, Winner: {winner}")
        # TODO: Add any final analysis here


# Helper functions you might find useful:

def is_winning_position(board, symbol):
    """
    Check if the given symbol has won on the board.

    Args:
        board: List of 9 strings representing the board state
        symbol: "X" or "O"

    Returns:
        True if symbol has won, False otherwise
    """
    # Winning combinations
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]

    for combo in wins:
        if all(board[i] == symbol for i in combo):
            return True
    return False


def find_winning_move(board, symbol):
    """
    Find a position that would win the game for symbol.

    Args:
        board: List of 9 strings representing the board state
        symbol: "X" or "O"

    Returns:
        Position (0-8) that would win, or None if no winning move
    """
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]

    for combo in wins:
        values = [board[i] for i in combo]
        # Check if two are the symbol and one is empty
        if values.count(symbol) == 2 and values.count("") == 1:
            # Return the empty position
            for i in combo:
                if board[i] == "":
                    return i
    return None


def get_empty_positions(board):
    """
    Get all empty positions on the board.

    Args:
        board: List of 9 strings representing the board state

    Returns:
        List of positions (0-8) that are empty
    """
    return [i for i, cell in enumerate(board) if cell == ""]


if __name__ == "__main__":
    # TODO: Update the class name here if you renamed your player class
    player_main_loop(MyTicTacToePlayer)
