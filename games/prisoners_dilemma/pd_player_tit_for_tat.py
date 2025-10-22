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
    from base_player import BasePlayer, debug, player_main_loop
except ImportError:
    # Fallback for when running in Docker with base_player.py mounted
    import base_player
    BasePlayer = base_player.BasePlayer
    debug = base_player.debug
    player_main_loop = base_player.player_main_loop


class TitForTatPlayer(BasePlayer):
    """
    Implements the Tit-for-Tat strategy for Prisoner's Dilemma.
    Tracks full game history including moves and scores.
    """

    def __init__(self):
        super().__init__()
        self.my_moves = []
        self.opponent_moves = []
        self.scores_per_round = []
        self.total_rounds = 0
        self.current_score = 0

    def on_game_start(self, message):
        """Initialize game state when game starts."""
        self.total_rounds = message.get("rounds")
        rules = message.get("rules", {})
        debug(f"Game starting! Playing {self.total_rounds} rounds - Tit-for-Tat strategy")
        debug(f"Rules: {rules}")

    def on_your_turn(self, message):
        """
        Make a move using Tit-for-Tat strategy.
        Returns 'C' for cooperate or 'D' for defect.
        """
        round_num = message.get("round")
        self.current_score = message.get("your_score")
        last_round = message.get("last_round")

        if last_round:
            # Track history from last round
            opponent_last_move = last_round['opponent_move']
            my_last_move = last_round['your_move']
            score_gained = last_round['your_score_gained']

            self.opponent_moves.append(opponent_last_move)
            self.my_moves.append(my_last_move)
            self.scores_per_round.append(score_gained)

            debug(f"Round {round_num}: Score={self.current_score}, "
                  f"Last: I played {my_last_move}, "
                  f"Opponent played {opponent_last_move}, "
                  f"I gained {score_gained}")

            # Tit-for-tat: copy opponent's last move
            my_move = opponent_last_move
            debug(f"Choosing: {'COOPERATE' if my_move == 'C' else 'DEFECT'} (copying opponent)")
        else:
            # First round: cooperate
            my_move = "C"
            debug(f"Round {round_num}: Score={self.current_score} (first round)")
            debug("Choosing: COOPERATE (first round)")

        return my_move

    def on_game_over(self, message):
        """Called when game ends. Print game statistics."""
        result = message.get("result")
        final_scores = message.get("final_scores")
        debug(f"Game over! Result: {result}")
        debug(f"Final scores: {final_scores}")
        debug(f"My move history: {self.my_moves}")
        debug(f"Opponent move history: {self.opponent_moves}")
        debug(f"Scores per round: {self.scores_per_round}")
        debug(f"Total score: {self.current_score}")


if __name__ == "__main__":
    player_main_loop(TitForTatPlayer)
