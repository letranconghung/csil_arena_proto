#!/usr/bin/env python3
"""
Prisoner's Dilemma player that always cooperates.
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


def handle_message(message):
    """Handle messages from the manager."""
    msg_type = message.get("type")

    if msg_type == "game_start":
        rounds = message.get("rounds")
        debug(f"Game starting! Playing {rounds} rounds - Always Cooperate strategy")
        return True

    elif msg_type == "your_turn":
        round_num = message.get("round")
        your_score = message.get("your_score")
        last_round = message.get("last_round")

        if last_round:
            debug(f"Round {round_num}: Score={your_score}, "
                  f"Last: I played {last_round['your_move']}, "
                  f"Opponent played {last_round['opponent_move']}, "
                  f"I gained {last_round['your_score_gained']}")
        else:
            debug(f"Round {round_num}: Score={your_score} (first round)")

        # Always cooperate
        debug("Choosing: COOPERATE")
        send_message({"move": "C"})
        return True

    elif msg_type == "game_over":
        result = message.get("result")
        final_scores = message.get("final_scores")
        debug(f"Game over! Result: {result}")
        debug(f"Final scores: {final_scores}")
        return False

    elif msg_type == "error":
        error_msg = message.get("message")
        debug(f"Error from manager: {error_msg}")
        return True

    return True


if __name__ == "__main__":
    player_main_loop(handle_message)
