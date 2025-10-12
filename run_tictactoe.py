#!/usr/bin/env python3
"""
Entry point for running a Tic-Tac-Toe game.
"""
import sys
import os
import time
from core.local_player_container import LocalPlayerContainer
# from core.player_container import PlayerContainer as LocalPlayerContainer
from games.tictactoe.tictactoe_manager import TicTacToeManager


def main():
    if len(sys.argv) < 3:
        print("Usage: python run_tictactoe.py <player1_script> <player2_script> [--verbose]")
        print("\nExample:")
        print("  python run_tictactoe.py games/tictactoe/tictactoe_player.py games/tictactoe/tictactoe_player_blocking.py")
        print("  python run_tictactoe.py games/tictactoe/tictactoe_player.py games/tictactoe/tictactoe_player_blocking.py --verbose")
        sys.exit(1)

    # Parse arguments
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    args = [arg for arg in sys.argv[1:] if arg not in ["--verbose", "-v"]]

    player1_script = os.path.abspath(args[0])
    player2_script = os.path.abspath(args[1])

    # Validate scripts exist
    if not os.path.exists(player1_script):
        print(f"Error: Player 1 script not found: {player1_script}", file=sys.stderr)
        sys.exit(1)
    if not os.path.exists(player2_script):
        print(f"Error: Player 2 script not found: {player2_script}", file=sys.stderr)
        sys.exit(1)

    print("=== TIC-TAC-TOE GAME ===\n")

    # Create game manager
    game = TicTacToeManager()

    # Create player containers
    print("Starting Player 1 (X)...")
    player1 = LocalPlayerContainer("player1", timeout=10.0)
    player1.start(player1_script)

    print("Starting Player 2 (O)...")
    player2 = LocalPlayerContainer("player2", timeout=10.0)
    player2.start(player2_script)

    game.players = {"player1": player1, "player2": player2}

    try:
        # Initialize game
        game.initialize_game()

        # Wait for both players to be ready
        print("\nWaiting for players to be ready...")
        for player_id, player in game.players.items():
            response = player.receive_message()
            if response.get("status") == "ready":
                print(f"  {player_id} is ready")

                # Show debug messages if verbose
                if verbose:
                    for debug_msg in player.get_debug_messages():
                        print(f"  [{player_id} LOG] {debug_msg}")
                else:
                    player.get_debug_messages()  # Clear the queue

        # Send game start messages
        print("\nStarting game...\n")
        for player_id, player in game.players.items():
            player.send_message(game.get_initial_message(player_id))

        # Brief pause for game start messages
        time.sleep(0.1)
        for player_id, player in game.players.items():
            if verbose:
                for debug_msg in player.get_debug_messages():
                    print(f"[{player_id} LOG] {debug_msg}")
            else:
                player.get_debug_messages()  # Clear the queue

        # Game loop
        move_count = 0
        while not game.is_game_over():
            # Get next players (should be one for turn-based)
            next_players = game.get_next_player_ids()
            if not next_players:
                break

            for player_id in next_players:
                player = game.players[player_id]
                move_count += 1

                print(f"\n--- Move {move_count}: {player_id} ({game.player_symbols[player_id]}) ---")
                print(game.get_display_state())

                # Send move request
                player.send_message(game.get_move_request_message(player_id))

                # Receive move with timeout
                try:
                    response = player.receive_message()
                    move = response.get("move")

                    # Show debug messages if verbose
                    if verbose:
                        for debug_msg in player.get_debug_messages():
                            print(f"[{player_id} LOG] {debug_msg}")
                    else:
                        player.get_debug_messages()  # Clear the queue

                    # Validate and apply move
                    valid, error_msg = game.validate_move(player_id, move)
                    if not valid:
                        print(f"Invalid move by {player_id}: {error_msg}")
                        # End game with other player winning
                        opponent_id = "player2" if player_id == "player1" else "player1"
                        game.winner = game.player_symbols[opponent_id]
                        game.result_message = f"{player_id} made invalid move"
                        break

                    print(f"{player_id} played position {move}")
                    game.apply_move(player_id, move)

                except TimeoutError:
                    print(f"\n{player_id} timed out")
                    opponent_id = "player2" if player_id == "player1" else "player1"
                    game.winner = game.player_symbols[opponent_id]
                    game.result_message = f"{player_id} timed out"
                    break

                except Exception as e:
                    print(f"\nError from {player_id}: {e}", file=sys.stderr)
                    opponent_id = "player2" if player_id == "player1" else "player1"
                    game.winner = game.player_symbols[opponent_id]
                    game.result_message = f"{player_id} error"
                    break

        # Game over
        result = game.get_game_result()
        print(f"\n{'='*40}")
        print(f"GAME OVER: {result['result']}")
        print(game.get_display_state())

        # Send game over messages
        for player_id, player in game.players.items():
            player.send_message({
                "type": "game_over",
                **result
            })

        # Wait briefly and collect final debug messages
        time.sleep(0.2)
        if verbose:
            print("\n--- Final logs ---")
            for player_id, player in game.players.items():
                for debug_msg in player.get_debug_messages():
                    print(f"[{player_id} LOG] {debug_msg}")
        else:
            # Clear debug message queues
            for player in game.players.values():
                player.get_debug_messages()

    except KeyboardInterrupt:
        print("\n\nGame interrupted by user")
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
    finally:
        print("\nStopping players...")
        for player in game.players.values():
            player.stop()
        print("Done!")


if __name__ == "__main__":
    main()
