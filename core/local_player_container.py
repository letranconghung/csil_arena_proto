#!/usr/bin/env python3
"""
LocalPlayerContainer class for running player scripts as subprocesses without Docker.
Used for distribution where users test their player scripts locally.
"""
import subprocess
import json
import threading
import queue
import select
from typing import Dict, Any


class LocalPlayerContainer:
    """Manages a player script running as a local subprocess (no Docker)."""

    def __init__(self, player_id: str, timeout: float = 10.0):
        """
        Initialize a local player container.

        Args:
            player_id: Unique identifier for this player
            timeout: Default timeout for receiving messages in seconds
        """
        self.player_id = player_id
        self.timeout = timeout
        self.process = None
        self.stderr_thread = None
        self.stderr_queue = queue.Queue()

    def start(self, player_script: str) -> None:
        """
        Start the player script as a subprocess.

        Args:
            player_script: Absolute path to the player script to run
        """
        import sys

        # Run player script with Python
        cmd = [sys.executable, "-u", player_script]

        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        # Start thread to capture stderr (debug messages)
        self.stderr_thread = threading.Thread(
            target=self._read_stderr,
            daemon=True
        )
        self.stderr_thread.start()

    def _read_stderr(self) -> None:
        """Read stderr in a separate thread."""
        try:
            for line in self.process.stderr:
                self.stderr_queue.put(line.strip())
        except:
            pass

    def send_message(self, message: Dict[str, Any]) -> None:
        """
        Send a JSON message to the player.

        Args:
            message: Dictionary to send as JSON
        """
        self.process.stdin.write(json.dumps(message) + "\n")
        self.process.stdin.flush()

    def receive_message(self, timeout: float = None) -> Dict[str, Any]:
        """
        Receive a JSON message from the player with timeout.

        Args:
            timeout: Timeout in seconds (uses default if None)

        Returns:
            Parsed JSON message as dictionary

        Raises:
            TimeoutError: If player doesn't respond in time
            RuntimeError: If player disconnects
            json.JSONDecodeError: If response is not valid JSON
        """
        if timeout is None:
            timeout = self.timeout

        # Use select to implement timeout
        ready, _, _ = select.select([self.process.stdout], [], [], timeout)

        if not ready:
            raise TimeoutError(f"Player {self.player_id} timed out")

        line = self.process.stdout.readline().strip()
        if not line:
            raise RuntimeError(f"Player {self.player_id} disconnected")

        return json.loads(line)

    def get_debug_messages(self) -> list:
        """
        Get all pending debug messages from stderr.

        Returns:
            List of debug message strings
        """
        messages = []
        while not self.stderr_queue.empty():
            try:
                messages.append(self.stderr_queue.get_nowait())
            except queue.Empty:
                break
        return messages

    def stop(self) -> None:
        """Stop the subprocess gracefully."""
        if self.process:
            try:
                self.process.stdin.close()
                self.process.wait(timeout=5)
            except:
                # Force kill if graceful shutdown fails
                self.process.kill()
