#!/usr/bin/env python3
"""
Simple tic-tac-toe player that picks the first empty cell.
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


def handle_message(message):
    """Handle messages from the manager."""
    global board, my_symbol, opponent_symbol

    msg_type = message.get("type")

    if msg_type == "game_start":
        my_symbol = message.get("symbol")
        opponent_symbol = "O" if my_symbol == "X" else "X"
        debug(f"Game starting! I am player '{my_symbol}'")
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

        # Simple AI: find first empty cell
        move = None
        for i, cell in enumerate(board):
            if cell == "":
                move = i
                break

        if move is not None:
            debug(f"Choosing move: {move}")
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
