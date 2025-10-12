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
    from base_player import debug, send_message, player_main_loop
except ImportError:
    # Fallback for when running in Docker with base_player.py mounted
    import base_player
    debug = base_player.debug
    send_message = base_player.send_message
    player_main_loop = base_player.player_main_loop


# Game state
board = [""] * 9
my_symbol = None
opponent_symbol = None


def check_winning_move(board_state, symbol):
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
        values = [board_state[i] for i in combo]
        # Check if two are the symbol and one is empty
        if values.count(symbol) == 2 and values.count("") == 1:
            # Return the empty position
            for i in combo:
                if board_state[i] == "":
                    return i
    return None


def choose_move(board_state, my_sym, opp_sym):
    """Choose the best move using blocking strategy."""
    # 1. Prefer center if available
    if board_state[4] == "":
        debug("Choosing center")
        return 4

    # 2. Check if we can win
    winning_move = check_winning_move(board_state, my_sym)
    if winning_move is not None:
        debug(f"Found winning move: {winning_move}")
        return winning_move

    # 3. Block opponent's winning move
    blocking_move = check_winning_move(board_state, opp_sym)
    if blocking_move is not None:
        debug(f"Blocking opponent at: {blocking_move}")
        return blocking_move

    # 4. Prefer corners
    corners = [0, 2, 6, 8]
    for corner in corners:
        if board_state[corner] == "":
            debug(f"Choosing corner: {corner}")
            return corner

    # 5. Take any available space
    for i, cell in enumerate(board_state):
        if cell == "":
            debug(f"Choosing first available: {i}")
            return i

    return None


def handle_message(message):
    """Handle messages from the manager."""
    global board, my_symbol, opponent_symbol

    msg_type = message.get("type")

    if msg_type == "game_start":
        my_symbol = message.get("symbol")
        opponent_symbol = "O" if my_symbol == "X" else "X"
        debug(f"Game starting! I am player '{my_symbol}' (blocking strategy)")
        return True

    elif msg_type == "your_turn":
        time_index = message.get("time_index")
        opponent_move = message.get("opponent_move")

        # Update board with opponent's move if present
        if opponent_move is not None:
            pos = opponent_move["position"]
            symbol = opponent_move["symbol"]
            board[pos] = symbol
            debug(f"Opponent played {symbol} at position {pos}")

        debug(f"Time index: {time_index}, Board: {board}")

        # Use blocking strategy
        move = choose_move(board, my_symbol, opponent_symbol)

        if move is not None:
            # Update local board state
            board[move] = my_symbol
            send_message({"move": move})
        else:
            debug("No valid moves available")
            send_message({"move": -1})

        return True

    elif msg_type == "game_over":
        result = message.get("result")
        winner = message.get("winner")
        debug(f"Game over! Result: {result}, Winner: {winner}")
        return False

    elif msg_type == "error":
        error_msg = message.get("message")
        debug(f"Error from manager: {error_msg}")
        return True

    return True


if __name__ == "__main__":
    player_main_loop(handle_message)
