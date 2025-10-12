#!/usr/bin/env python3
"""
Prisoner's Dilemma player using Tit-for-Tat strategy.
- Cooperates on the first round
- Then copies opponent's previous move
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
        debug(f"Game starting! Playing {rounds} rounds - Tit-for-Tat strategy")
        return True

    elif msg_type == "your_turn":
        round_num = message.get("round")
        your_score = message.get("your_score")
        last_round = message.get("last_round")

        if last_round:
            opponent_last_move = last_round['opponent_move']
            debug(f"Round {round_num}: Score={your_score}, "
                  f"Last: I played {last_round['your_move']}, "
                  f"Opponent played {opponent_last_move}, "
                  f"I gained {last_round['your_score_gained']}")

            # Tit-for-tat: copy opponent's last move
            my_move = opponent_last_move
            debug(f"Choosing: {'COOPERATE' if my_move == 'C' else 'DEFECT'} (copying opponent)")
        else:
            # First round: cooperate
            my_move = "C"
            debug(f"Round {round_num}: Score={your_score} (first round)")
            debug("Choosing: COOPERATE (first round)")

        send_message({"move": my_move})
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
