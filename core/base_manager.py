#!/usr/bin/env python3
"""
Abstract base class for game managers.
Defines the interface that all game-specific managers must implement.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple


class GameManager(ABC):
    """
    Abstract base class for managing a game between players.

    Subclasses must implement game-specific logic while the base class
    handles common functionality like player management and communication.
    """

    def __init__(self):
        """Initialize the game manager."""
        self.players = {}  # player_id -> PlayerContainer
        self.game_state = None

    @abstractmethod
    def initialize_game(self) -> None:
        """
        Initialize the game state.
        Called once at the start of the game.
        """
        pass

    @abstractmethod
    def get_initial_message(self, player_id: str) -> Dict[str, Any]:
        """
        Get the initial game_start message to send to a player.

        Args:
            player_id: The ID of the player

        Returns:
            Dictionary containing the game_start message
        """
        pass

    @abstractmethod
    def should_request_moves_simultaneously(self) -> bool:
        """
        Determine if moves should be requested simultaneously or sequentially.

        Returns:
            True for simultaneous (e.g., Prisoner's Dilemma)
            False for turn-based (e.g., Tic-Tac-Toe)
        """
        pass

    @abstractmethod
    def get_next_player_ids(self) -> List[str]:
        """
        Get the list of player IDs who should move next.

        For turn-based games, returns a single-element list.
        For simultaneous games, returns all player IDs.

        Returns:
            List of player IDs who should make a move
        """
        pass

    @abstractmethod
    def get_move_request_message(self, player_id: str) -> Dict[str, Any]:
        """
        Create the message to request a move from a player.

        Args:
            player_id: The ID of the player

        Returns:
            Dictionary containing the move request message
        """
        pass

    @abstractmethod
    def validate_move(self, player_id: str, move_data: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate a move from a player.

        Args:
            player_id: The ID of the player making the move
            move_data: The move data from the player

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is None
        """
        pass

    @abstractmethod
    def apply_move(self, player_id: str, move_data: Any) -> None:
        """
        Apply a validated move to the game state.

        Args:
            player_id: The ID of the player making the move
            move_data: The move data from the player
        """
        pass

    @abstractmethod
    def is_game_over(self) -> bool:
        """
        Check if the game has ended.

        Returns:
            True if the game is over, False otherwise
        """
        pass

    @abstractmethod
    def get_game_result(self) -> Dict[str, Any]:
        """
        Get the final result of the game.

        Returns:
            Dictionary containing game result information
            Should include 'result' key with human-readable result
        """
        pass

    @abstractmethod
    def get_display_state(self) -> str:
        """
        Get a human-readable representation of the current game state.

        Returns:
            String representation for console display
        """
        pass

    def get_player_timeout(self, player_id: str) -> float:
        """
        Get the timeout for a player's move in seconds.

        Can be overridden by subclasses for game-specific timeouts.

        Args:
            player_id: The ID of the player

        Returns:
            Timeout in seconds (default: 10.0)
        """
        return 10.0
