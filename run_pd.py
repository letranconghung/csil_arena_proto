#!/usr/bin/env python3
"""
Entry point for running a Prisoner's Dilemma game.
"""
import sys
import os
import time
import threading
from core.local_player_container import LocalPlayerContainer
# from core.player_container import PlayerContainer as LocalPlayerContainer
from games.pd.pd_manager import PrisonersDilemmaManager


def main():
    if len(sys.argv) < 3:
        print("Usage: python run_prisoners_dilemma.py <player1_script> <player2_script> [--verbose]")
        print("\nExample:")
        print("  python run_prisoners_dilemma.py games/prisoners_dilemma/pd_player_always_cooperate.py games/prisoners_dilemma/pd_player_tit_for_tat.py")
        print("  python run_prisoners_dilemma.py games/prisoners_dilemma/pd_player_always_cooperate.py games/prisoners_dilemma/pd_player_tit_for_tat.py --verbose")
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

    print("=== PRISONER'S DILEMMA GAME ===\n")

    # Create game manager
    game = PrisonersDilemmaManager()

    player1 = LocalPlayerContainer("player1", timeout=10.0)
    player1.start(player1_script)

    player2 = LocalPlayerContainer("player2", timeout=10.0)
    player2.start(player2_script)

    game.players = {"player1": player1, "player2": player2}

    try:
        # Initialize game
        game.initialize_game()

        # Wait for both players to be ready
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

        # Game loop (simultaneous moves)
        while not game.is_game_over():
            next_players = game.get_next_player_ids()
            if not next_players:
                break

            # Request moves from all players simultaneously
            for player_id in next_players:
                player = game.players[player_id]
                player.send_message(game.get_move_request_message(player_id))

                # Clear any debug messages before collecting moves
                if verbose:
                    for debug_msg in player.get_debug_messages():
                        print(f"  [{player_id} LOG] {debug_msg}")
                else:
                    player.get_debug_messages()  # Clear the queue

            # Collect moves with threads (simultaneous)
            moves = {}
            errors = {}

            def collect_move(pid):
                try:
                    player = game.players[pid]
                    response = player.receive_message()
                    move = response.get("move")

                    # Validate move
                    valid, error_msg = game.validate_move(pid, move)
                    if not valid:
                        errors[pid] = error_msg
                    else:
                        moves[pid] = move

                except TimeoutError:
                    errors[pid] = "timed out"
                except Exception as e:
                    errors[pid] = str(e)

            # Start threads to collect moves
            threads = []
            for player_id in next_players:
                thread = threading.Thread(target=collect_move, args=(player_id,))
                thread.start()
                threads.append(thread)

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Check for errors
            if errors:
                print("\nErrors occurred:")
                for pid, error in errors.items():
                    print(f"  {pid}: {error}")
                break

            # Apply moves
            for player_id, move in moves.items():
                game.apply_move(player_id, move)

            # Process simultaneous moves (calculate scores)
            game.process_simultaneous_moves()

            # Show debug messages
            for player_id in next_players:
                player = game.players[player_id]
                if verbose:
                    for debug_msg in player.get_debug_messages():
                        print(f"  [{player_id} LOG] {debug_msg}")
                else:
                    player.get_debug_messages()  # Clear the queue

        # Game over
        result = game.get_game_result()
        print(f"\n{'='*40}")
        print(f"GAME OVER: {result['result']}")
        print(f"\nFinal Scores:")
        for player_id, score in result['final_scores'].items():
            print(f"  {player_id}: {score}")

        # Display move table
        print(f"\n{'='*40}")
        print("MOVE HISTORY:")
        print(f"{'='*40}")

        # Header
        player1_id = game.player_ids[0]
        player2_id = game.player_ids[1]
        print(f"Round | {player1_id:^10} | {player2_id:^10}")
        print(f"{'-'*6}|{'-'*12}|{'-'*12}")

        # Display each round's moves
        for round_num, (p1_move, p2_move, p1_score, p2_score) in enumerate(game.history, 1):
            print(f"{round_num:^6}| {p1_move:^10} | {p2_move:^10}")

        # Display totals
        print(f"{'-'*6}|{'-'*12}|{'-'*12}")
        print(f"TOTAL | {result['final_scores'][player1_id]:^10} | {result['final_scores'][player2_id]:^10}")
        print(f"{'='*40}")

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
