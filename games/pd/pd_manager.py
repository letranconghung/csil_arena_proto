#!/usr/bin/env python3
"""
Prisoner's Dilemma game manager implementation.
100 rounds of simultaneous cooperation/defection decisions.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from core.base_manager import GameManager
from typing import Dict, Any, List, Tuple, Optional


class PrisonersDilemmaManager(GameManager):
    """Manager for a Prisoner's Dilemma game between two players."""

    # Payoff matrix
    COOPERATE = "C"
    DEFECT = "D"
    ROUNDS = 100

    def __init__(self):
        super().__init__()
        self.current_round = 0
        self.scores = {}  # player_id -> cumulative score
        self.history = []  # List of (player1_move, player2_move, player1_score, player2_score)
        self.current_moves = {}  # player_id -> move (for current round)
        self.player_ids = []

    def initialize_game(self) -> None:
        """Initialize the Prisoner's Dilemma game state."""
        self.current_round = 0
        self.history = []
        self.current_moves = {}

        # Initialize scores
        player_ids = list(self.players.keys())
        if len(player_ids) != 2:
            raise ValueError("Prisoner's Dilemma requires exactly 2 players")

        self.player_ids = player_ids
        for player_id in player_ids:
            self.scores[player_id] = 0

    def get_initial_message(self, player_id: str) -> Dict[str, Any]:
        """Get the initial game_start message for a player."""
        return {
            "type": "game_start",
            "game": "prisoners_dilemma",
            "rounds": self.ROUNDS,
            "rules": {
                "both_cooperate": {"you": 3, "opponent": 3},
                "you_cooperate_opponent_defects": {"you": 0, "opponent": 5},
                "you_defect_opponent_cooperates": {"you": 5, "opponent": 0},
                "both_defect": {"you": 1, "opponent": 1}
            }
        }

    def should_request_moves_simultaneously(self) -> bool:
        """Prisoner's Dilemma requires simultaneous moves."""
        return True

    def get_next_player_ids(self) -> List[str]:
        """Both players move simultaneously."""
        if self.current_round < self.ROUNDS:
            return self.player_ids
        return []

    def get_move_request_message(self, player_id: str) -> Dict[str, Any]:
        """Create the move request message for a player."""
        message = {
            "type": "your_turn",
            "round": self.current_round + 1,
            "your_score": self.scores[player_id]
        }

        # Include opponent's last move if available
        if self.history:
            last_round = self.history[-1]
            # Determine which player this is
            player_idx = self.player_ids.index(player_id)
            opponent_idx = 1 - player_idx

            opponent_move = last_round[opponent_idx]
            your_last_move = last_round[player_idx]
            your_last_score = last_round[2 + player_idx]

            message["last_round"] = {
                "your_move": your_last_move,
                "opponent_move": opponent_move,
                "your_score_gained": your_last_score
            }

        return message

    def validate_move(self, player_id: str, move_data: Any) -> Tuple[bool, Optional[str]]:
        """Validate a move from a player."""
        if not isinstance(move_data, str):
            return False, f"Move must be a string, got {type(move_data)}"

        move_upper = move_data.upper()
        if move_upper not in [self.COOPERATE, self.DEFECT]:
            return False, f"Move must be 'C' (cooperate) or 'D' (defect), got {move_data}"

        return True, None

    def apply_move(self, player_id: str, move_data: Any) -> None:
        """Store the move (not applied until both players have moved)."""
        self.current_moves[player_id] = move_data.upper()

    def is_game_over(self) -> bool:
        """Check if all rounds have been played."""
        return self.current_round >= self.ROUNDS

    def get_game_result(self) -> Dict[str, Any]:
        """Get the final result of the game."""
        # Determine winner
        player1_score = self.scores[self.player_ids[0]]
        player2_score = self.scores[self.player_ids[1]]

        if player1_score > player2_score:
            winner = self.player_ids[0]
            result_msg = f"{self.player_ids[0]} wins with {player1_score} points"
        elif player2_score > player1_score:
            winner = self.player_ids[1]
            result_msg = f"{self.player_ids[1]} wins with {player2_score} points"
        else:
            winner = None
            result_msg = f"Draw with {player1_score} points each"

        return {
            "result": result_msg,
            "winner": winner,
            "final_scores": self.scores,
            "history": self.history
        }

    def get_display_state(self) -> str:
        """Get a human-readable representation of the current game state."""
        lines = [f"\nRound {self.current_round}/{self.ROUNDS}"]
        lines.append(f"Scores: {self.player_ids[0]}={self.scores[self.player_ids[0]]}, "
                    f"{self.player_ids[1]}={self.scores[self.player_ids[1]]}")
        return "\n".join(lines)

    def process_simultaneous_moves(self) -> None:
        """
        Process moves from both players after they've both submitted.
        Calculate scores based on payoff matrix.
        """
        if len(self.current_moves) != 2:
            raise RuntimeError("Not all players have submitted moves")

        player1_move = self.current_moves[self.player_ids[0]]
        player2_move = self.current_moves[self.player_ids[1]]

        # Calculate scores based on payoff matrix
        if player1_move == self.COOPERATE and player2_move == self.COOPERATE:
            player1_score = 3
            player2_score = 3
        elif player1_move == self.COOPERATE and player2_move == self.DEFECT:
            player1_score = 0
            player2_score = 5
        elif player1_move == self.DEFECT and player2_move == self.COOPERATE:
            player1_score = 5
            player2_score = 0
        else:  # Both defect
            player1_score = 1
            player2_score = 1

        # Update cumulative scores
        self.scores[self.player_ids[0]] += player1_score
        self.scores[self.player_ids[1]] += player2_score

        # Record history
        self.history.append((player1_move, player2_move, player1_score, player2_score))

        # Clear current moves and advance round
        self.current_moves = {}
        self.current_round += 1
