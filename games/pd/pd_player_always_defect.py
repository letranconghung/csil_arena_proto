#!/usr/bin/env python3
"""
Prisoner's Dilemma player that always defects.
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


class AlwaysDefectPlayer(BasePlayer):
    """
    Always defects regardless of opponent's actions.
    Tracks game history for analysis.
    """

    def __init__(self):
        super().__init__()
        self.rounds_played = 0
        self.total_rounds = 0

    def on_game_start(self, message):
        """Initialize game state when game starts."""
        self.total_rounds = message.get("rounds")

    def on_your_turn(self, message):
        """
        Always returns 'D' for defect.
        """
        round_num = message.get("round")
        your_score = message.get("your_score")
        last_round = message.get("last_round")

        # Always defect
        self.rounds_played += 1
        return "D"

    def on_game_over(self, message):
        """Called when game ends."""
        result = message.get("result")
        final_scores = message.get("final_scores")


if __name__ == "__main__":
    player_main_loop(AlwaysDefectPlayer)
