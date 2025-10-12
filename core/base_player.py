#!/usr/bin/env python3
"""
Base player utilities for creating player scripts.
Provides common functionality for communication and debugging.
"""
import sys
import json
from typing import Dict, Any


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


def receive_message() -> Dict[str, Any]:
    """
    Receive a JSON message from the manager via stdin.

    Returns:
        Parsed JSON message as dictionary

    Raises:
        EOFError: If stdin is closed
        json.JSONDecodeError: If message is not valid JSON
    """
    line = sys.stdin.readline().strip()
    if not line:
        raise EOFError("No message received")
    return json.loads(line)


def setup_io() -> None:
    """
    Configure stdin/stdout/stderr for immediate communication.
    Should be called at the start of main().
    """
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)


def player_main_loop(handle_message_func) -> None:
    """
    Main loop for player scripts.

    Args:
        handle_message_func: Function that takes a message dict and handles it.
                            Should return True to continue, False to exit.

    Example:
        def handle_message(msg):
            if msg["type"] == "game_over":
                return False
            # ... handle other messages
            return True

        player_main_loop(handle_message)
    """
    setup_io()
    debug("Player initializing")
    send_message({"status": "ready"})

    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
                should_continue = handle_message_func(message)
                if not should_continue:
                    break

            except json.JSONDecodeError as e:
                debug(f"Failed to parse JSON: {line}, error: {e}")
            except Exception as e:
                debug(f"Error processing message: {e}")

    except KeyboardInterrupt:
        debug("Interrupted")

    debug("Player shutting down")
