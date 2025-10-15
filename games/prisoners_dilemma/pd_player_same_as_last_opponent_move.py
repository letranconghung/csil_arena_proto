#!/usr/bin/env python3
"""
TEMPLATE: Prisoner's Dilemma Player

This is a template for creating your own Prisoner's Dilemma player.
Replace the TODO sections with your strategy implementation.

GAME RULES:
- 30 rounds of decisions between two players
- Each round, choose: "C" (cooperate) or "D" (defect)
- Payoff matrix:
  * Both cooperate: 3 points each
  * You cooperate, opponent defects: 0 points (you), 5 points (opponent)
  * You defect, opponent cooperates: 5 points (you), 0 points (opponent)
  * Both defect: 1 point each
"""
import sys
import os

# Add core directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../core'))

from base_player import BasePlayer, debug, player_main_loop


class MyPrisonersDilemmaPlayer(BasePlayer):
    """
    TODO: Give your player class a descriptive name and document your strategy here.

    Example strategies you could implement:
    - Always cooperate
    - Always defect
    - Tit-for-tat (copy opponent's last move)
    - Random choice
    - Pattern detection
    - Adaptive strategy based on opponent behavior
    """

    def __init__(self):
        """
        Initialize your player.

        TODO: Add any instance variables you need to track state.

        Examples:
        - self.opponent_moves = []  # Track opponent's move history
        - self.my_moves = []        # Track your own moves
        - self.round_count = 0      # Track which round we're on
        """
        super().__init__()
        # TODO: Initialize your state variables here
        pass

    def on_game_start(self, message):
        """
        Called once at the start of the game.

        INPUT (message dict):
        {
            "type": "game_start",
            "game": "prisoners_dilemma",
            "rounds": 30,
            "rules": {
                "both_cooperate": {"you": 3, "opponent": 3},
                "you_cooperate_opponent_defects": {"you": 0, "opponent": 5},
                "you_defect_opponent_cooperates": {"you": 5, "opponent": 0},
                "both_defect": {"you": 1, "opponent": 1}
            }
        }

        TODO: Use this to initialize any strategy-specific state.
        """
        debug("Game starting!")
        # TODO: Add your initialization logic here
        pass

    def on_your_turn(self, message):
        """
        Called each round to get your move.

        INPUT (message dict):
        Round 1:
        {
            "type": "your_turn",
            "round": 1,
            "your_score": 0
        }

        Round 2+:
        {
            "type": "your_turn",
            "round": 2,
            "your_score": 3,  # Your cumulative score
            "last_round": {
                "your_move": "C",           # What you played last round
                "opponent_move": "C",       # What opponent played last round
                "your_score_gained": 3      # Points you gained last round
            }
        }

        OUTPUT: Return either "C" (cooperate) or "D" (defect)

        TODO: Implement your strategy here.
        """
        # TODO: Implement your decision logic here

        # Example: Access information from the message
        round_num = message.get("round")
        your_score = message.get("your_score")
        last_round = message.get("last_round")

        if last_round:
            # Not the first round - we have history
            opponent_last_move = last_round["opponent_move"]
            my_last_move = last_round["your_move"]
            debug(f"Round {round_num}: Opponent played {opponent_last_move}, I played {my_last_move}")

            # TODO: Make decision based on history
            my_move = opponent_last_move # Replace with your logic
        else:
            # First round - no history yet
            debug(f"Round {round_num}: First round")

            # TODO: Choose your first move
            my_move = "C"  # Replace with your logic

        debug(f"Choosing: {my_move}")
        return my_move

    def on_game_over(self, message):
        """
        Called once when the game ends.

        INPUT (message dict):
        {
            "type": "game_over",
            "result": "player1 wins with 95 points",
            "winner": "player1",
            "final_scores": {
                "player1": 95,
                "player2": 85
            },
            "history": [
                ("C", "D", 0, 5),  # Round 1: (p1_move, p2_move, p1_score, p2_score)
                ("D", "D", 1, 1),  # Round 2
                ...
            ]
        }

        TODO: Optional - add any cleanup or final analysis here.
        """
        result = message.get("result")
        debug(f"Game over! Result: {result}")
        # TODO: Add any final analysis here


if __name__ == "__main__":
    # TODO: Update the class name here if you renamed your player class
    player_main_loop(MyPrisonersDilemmaPlayer)
