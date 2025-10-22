#!/usr/bin/env python3
"""
Base player class for creating player scripts.
Provides minimal infrastructure for communication with the game manager.
"""
import sys
import json
from typing import Dict, Any
from abc import ABC, abstractmethod


def debug(message: str) -> None:
    """
    Send debug message to stderr for manager to capture.

    Args:
        message: Debug message to log
    """
    print(f"DEBUG: {message}", file=sys.stderr, flush=True)


def send_message(message: Dict[str, Any]) -> None:
    """
    Send a JSON message to the manager via stdout.

    Args:
        message: Dictionary to send as JSON
    """
    print(json.dumps(message), flush=True)


def setup_io() -> None:
    """Configure stdin/stdout/stderr for immediate communication."""
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)


class BasePlayer(ABC):
    """
    Minimal base class for player implementations.
    Handles message routing. Subclasses implement game logic.
    """

    @abstractmethod
    def on_game_start(self, message: Dict[str, Any]) -> None:
        """
        Called when the game starts.

        Args:
            message: Game start message containing game rules and parameters
        """
        pass

    @abstractmethod
    def on_your_turn(self, message: Dict[str, Any]) -> Any:
        """
        Called when it's your turn. Must return a move.

        Args:
            message: Turn message containing game state

        Returns:
            Your move (format depends on the game)
        """
        raise NotImplementedError("Subclasses must implement on_your_turn()")

    def on_game_over(self, message: Dict[str, Any]) -> None:
        """
        Called when the game ends. Override to perform cleanup or analysis.

        Args:
            message: Game over message containing result and final scores
        """
        pass

    def on_error(self, message: Dict[str, Any]) -> None:
        """
        Called when an error occurs. Override to handle errors differently.

        Args:
            message: Error message
        """
        error_msg = message.get("message")
        debug(f"Error from manager: {error_msg}")

    def handle_message(self, message: Dict[str, Any]) -> bool:
        """
        Internal message dispatcher. Routes messages to appropriate handlers.

        Args:
            message: Message from the game manager

        Returns:
            True to continue playing, False to exit
        """
        msg_type = message.get("type")

        if msg_type == "game_start":
            self.on_game_start(message)
            return True

        elif msg_type == "your_turn":
            move = self.on_your_turn(message)
            send_message({"move": move})
            return True

        elif msg_type == "game_over":
            self.on_game_over(message)
            return False

        elif msg_type == "error":
            self.on_error(message)
            return True

        return True


def player_main_loop(player_class: type) -> None:
    """
    Main loop for class-based player scripts.

    Args:
        player_class: The player class to instantiate (must subclass BasePlayer)

    Example:
        class MyPlayer(BasePlayer):
            def on_your_turn(self, message):
                return "some_move"

        if __name__ == "__main__":
            player_main_loop(MyPlayer)
    """
    setup_io()
    send_message({"status": "ready"})

    player = player_class()

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
                should_continue = player.handle_message(message)
                if not should_continue:
                    break

            except json.JSONDecodeError as e:
                debug(f"Failed to parse JSON: {line}, error: {e}")
            except Exception as e:
                debug(f"Error processing message: {e}")
                import traceback
                debug(traceback.format_exc())

    except KeyboardInterrupt:
        debug("Interrupted")

    debug("Player shutting down")
