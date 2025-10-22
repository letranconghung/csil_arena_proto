#!/usr/bin/env python3
"""
Tournament Manager for Prisoner's Dilemma.

Runs a round-robin tournament where each player plays against every other player
(excluding self-play) multiple times. Tracks total points and displays rankings.
"""
import sys
import os
import time
import threading
from typing import Dict, List, Tuple
from itertools import combinations
from core.local_player_container import LocalPlayerContainer
from games.pd.pd_manager import PrisonersDilemmaManager


class TournamentManager:
    """Manages a round-robin tournament for Prisoner's Dilemma."""

    def __init__(self, player_scripts: List[str], games_per_matchup: int = 5):
        """
        Initialize tournament.

        Args:
            player_scripts: List of absolute paths to player scripts
            games_per_matchup: Number of games each pair plays against each other
        """
        self.player_scripts = player_scripts
        self.games_per_matchup = games_per_matchup

        # Generate unique player names from script basenames
        self.player_names = self._generate_unique_names(player_scripts)

        # Track cumulative scores across all games
        self.total_scores = {name: 0 for name in self.player_names}
        self.wins = {name: 0 for name in self.player_names}
        self.draws = {name: 0 for name in self.player_names}
        self.losses = {name: 0 for name in self.player_names}
        self.games_played = {name: 0 for name in self.player_names}

        # Track individual game results
        self.game_results = []

        # Track timing information
        self.game_times = []  # Time for each game
        self.player_times = {name: 0.0 for name in self.player_names}  # Total time per player
        self.player_move_counts = {name: 0 for name in self.player_names}  # Number of moves per player

    def _generate_unique_names(self, player_scripts: List[str]) -> List[str]:
        """
        Generate unique player names from script paths.
        If duplicate basenames exist, add suffixes (_2, _3, etc.) to make them unique.

        Args:
            player_scripts: List of absolute paths to player scripts

        Returns:
            List of unique player names corresponding to the scripts
        """
        # Extract base names
        base_names = [os.path.basename(script).replace('.py', '') for script in player_scripts]

        # Track name occurrences
        name_counts = {}
        unique_names = []

        for base_name in base_names:
            if base_name not in name_counts:
                # First occurrence - use the name as-is
                name_counts[base_name] = 1
                unique_names.append(base_name)
            else:
                # Duplicate detected - add suffix
                name_counts[base_name] += 1
                unique_name = f"{base_name}_{name_counts[base_name]}"
                unique_names.append(unique_name)

        return unique_names

    def run_tournament(self) -> bool:
        """
        Run the full tournament.

        Returns:
            True if tournament completed successfully, False if player error occurred
        """
        # Start tournament timer
        tournament_start_time = time.time()

        print("=" * 80)
        print("PRISONER'S DILEMMA TOURNAMENT")
        print("=" * 80)
        print(f"\nPlayers ({len(self.player_names)}):")
        for i, name in enumerate(self.player_names, 1):
            print(f"  {i}. {name}")
        print(f"\nFormat: Round-robin, {self.games_per_matchup} games per matchup")

        # Generate all pairwise matchups (excluding self-play)
        matchups = list(combinations(range(len(self.player_scripts)), 2))
        total_games = len(matchups) * self.games_per_matchup

        print(f"Total matchups: {len(matchups)}")
        print(f"Total games: {total_games}")
        print("\n" + "=" * 80 + "\n")

        game_number = 0

        # Play each matchup
        for p1_idx, p2_idx in matchups:
            p1_script = self.player_scripts[p1_idx]
            p2_script = self.player_scripts[p2_idx]
            p1_name = self.player_names[p1_idx]
            p2_name = self.player_names[p2_idx]

            print(f"MATCHUP: {p1_name} vs {p2_name}")
            print("-" * 80)

            # Play multiple games for this matchup
            for game_num in range(self.games_per_matchup):
                game_number += 1
                print(f"\nGame {game_number}/{total_games} ({p1_name} vs {p2_name}, game {game_num + 1}/{self.games_per_matchup})")

                game_start_time = time.time()
                success, result = self.run_single_game(p1_script, p2_script, p1_name, p2_name)
                game_end_time = time.time()
                game_duration = game_end_time - game_start_time

                if not success:
                    print(f"\n{'=' * 80}")
                    print("TOURNAMENT ABORTED - Player error occurred")
                    print(f"{'=' * 80}")
                    return False

                # Track game timing
                self.game_times.append(game_duration)

                # Update player times
                self.player_times[p1_name] += result['player_times'][p1_name]
                self.player_times[p2_name] += result['player_times'][p2_name]
                self.player_move_counts[p1_name] += result['player_move_counts'][p1_name]
                self.player_move_counts[p2_name] += result['player_move_counts'][p2_name]

                # Update statistics
                self.update_stats(p1_name, p2_name, result)
                self.game_results.append({
                    'game_num': game_number,
                    'player1': p1_name,
                    'player2': p2_name,
                    'score1': result['scores'][p1_name],
                    'score2': result['scores'][p2_name],
                    'winner': result['winner']
                })

                # Print game result
                print(f"  Result: {result['result']}")
                print(f"  Scores: {p1_name}={result['scores'][p1_name]}, {p2_name}={result['scores'][p2_name]}")
                print(f"  Game time: {game_duration:.3f}s")

                # Calculate and show running averages
                p1_avg = self.total_scores[p1_name] / self.games_played[p1_name] if self.games_played[p1_name] > 0 else 0
                p2_avg = self.total_scores[p2_name] / self.games_played[p2_name] if self.games_played[p2_name] > 0 else 0
                print(f"  Averages: {p1_name}={p1_avg:.2f}, {p2_name}={p2_avg:.2f}")

            print()

        # Calculate total tournament time
        tournament_end_time = time.time()
        total_tournament_time = tournament_end_time - tournament_start_time

        print("\n" + "=" * 80)
        print("TOURNAMENT COMPLETE")
        print("=" * 80)
        self.print_final_rankings(total_tournament_time)
        return True

    def run_single_game(self, p1_script: str, p2_script: str, p1_name: str, p2_name: str) -> Tuple[bool, Dict]:
        """
        Run a single game between two players.

        Returns:
            (success, result_dict) - success is False if player error occurred
        """
        # Create game manager
        game = PrisonersDilemmaManager()

        # Use player names as IDs
        player1_id = p1_name
        player2_id = p2_name

        # Track player-specific timing
        player_times = {p1_name: 0.0, p2_name: 0.0}
        player_move_counts = {p1_name: 0, p2_name: 0}

        # Create player containers
        player1 = LocalPlayerContainer(player1_id, timeout=10.0)
        player2 = LocalPlayerContainer(player2_id, timeout=10.0)

        try:
            player1.start(p1_script)
            player2.start(p2_script)

            game.players = {player1_id: player1, player2_id: player2}
            game.initialize_game()

            # Wait for players to be ready
            for player_id, player in game.players.items():
                response = player.receive_message()
                if response.get("status") != "ready":
                    print(f"  ERROR: {player_id} did not send ready status")
                    return False, None
                player.get_debug_messages()  # Clear debug queue

            # Send game start messages
            for player_id, player in game.players.items():
                player.send_message(game.get_initial_message(player_id))

            time.sleep(0.05)
            for player in game.players.values():
                player.get_debug_messages()

            # Game loop (simultaneous moves)
            while not game.is_game_over():
                next_players = game.get_next_player_ids()
                if not next_players:
                    break

                # Request moves from all players simultaneously
                for player_id in next_players:
                    player = game.players[player_id]
                    player.send_message(game.get_move_request_message(player_id))
                    player.get_debug_messages()

                # Collect moves with threads
                moves = {}
                errors = {}
                move_times = {}

                def collect_move(pid):
                    try:
                        player = game.players[pid]
                        move_start = time.time()
                        response = player.receive_message()
                        move_end = time.time()
                        move_times[pid] = move_end - move_start

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

                # Wait for all threads
                for thread in threads:
                    thread.join()

                # Check for errors
                if errors:
                    print(f"  ERROR in game:")
                    for pid, error in errors.items():
                        print(f"    {pid}: {error}")
                    return False, None

                # Track timing for each player
                for pid, move_time in move_times.items():
                    # Map player ID back to actual player name
                    if pid == player1_id:
                        player_times[p1_name] += move_time
                        player_move_counts[p1_name] += 1
                    elif pid == player2_id:
                        player_times[p2_name] += move_time
                        player_move_counts[p2_name] += 1

                # Apply moves
                for player_id, move in moves.items():
                    game.apply_move(player_id, move)

                # Process simultaneous moves
                game.process_simultaneous_moves()

                # Clear debug messages
                for player in game.players.values():
                    player.get_debug_messages()

            # Game over - get results
            result = game.get_game_result()

            # Send game over messages
            for player_id, player in game.players.items():
                player.send_message({
                    "type": "game_over",
                    **result
                })

            time.sleep(0.05)
            for player in game.players.values():
                player.get_debug_messages()

            # Reformat result to use actual player names
            winner = result['winner']

            formatted_result = {
                'result': result['result'],
                'winner': winner,
                'scores': {
                    p1_name: result['final_scores'][player1_id],
                    p2_name: result['final_scores'][player2_id]
                },
                'player_times': player_times,
                'player_move_counts': player_move_counts
            }

            return True, formatted_result

        except Exception as e:
            print(f"  ERROR: Exception during game: {e}")
            import traceback
            traceback.print_exc()
            return False, None

        finally:
            # Always stop players
            player1.stop()
            player2.stop()

    def update_stats(self, p1_name: str, p2_name: str, result: Dict):
        """Update tournament statistics after a game."""
        p1_score = result['scores'][p1_name]
        p2_score = result['scores'][p2_name]

        # Update total scores
        self.total_scores[p1_name] += p1_score
        self.total_scores[p2_name] += p2_score

        # Update games played
        self.games_played[p1_name] += 1
        self.games_played[p2_name] += 1

        # Update win/draw/loss
        if result['winner'] == p1_name:
            self.wins[p1_name] += 1
            self.losses[p2_name] += 1
        elif result['winner'] == p2_name:
            self.wins[p2_name] += 1
            self.losses[p1_name] += 1
        else:  # Draw
            self.draws[p1_name] += 1
            self.draws[p2_name] += 1

    def print_final_rankings(self, total_tournament_time: float):
        """Print final tournament rankings and statistics."""
        print("\n" + "=" * 80)
        print("FINAL RANKINGS")
        print("=" * 80)

        # Sort players by average score per game (descending)
        rankings = sorted(
            self.player_names,
            key=lambda name: (
                self.total_scores[name] / self.games_played[name] if self.games_played[name] > 0 else 0,
                self.wins[name]
            ),
            reverse=True
        )

        # Print rankings table
        print(f"\n{'Rank':<6} {'Player':<30} {'Avg/Game':<10} {'Total':<8} {'Games':<8} {'W-D-L':<12}")
        print("-" * 80)

        for rank, name in enumerate(rankings, 1):
            points = self.total_scores[name]
            wins = self.wins[name]
            draws = self.draws[name]
            losses = self.losses[name]
            games = self.games_played[name]
            avg = points / games if games > 0 else 0

            wdl = f"{wins}-{draws}-{losses}"
            print(f"{rank:<6} {name:<30} {avg:<10.2f} {points:<8} {games:<8} {wdl:<12}")

        # Print timing statistics
        print("\n" + "=" * 80)
        print("TIMING STATISTICS")
        print("=" * 80)

        # Tournament-level timing
        avg_game_time = sum(self.game_times) / len(self.game_times) if self.game_times else 0
        print(f"\nTotal tournament time: {total_tournament_time:.3f}s ({total_tournament_time / 60:.2f} minutes)")
        print(f"Total games played: {len(self.game_times)}")
        print(f"Average time per game: {avg_game_time:.3f}s")

        # Player-level timing
        print(f"\n{'Player':<30} {'Total Time':<15} {'Avg per Move':<15} {'Move Count':<12}")
        print("-" * 80)

        for name in self.player_names:
            total_time = self.player_times[name]
            move_count = self.player_move_counts[name]
            avg_per_move = total_time / move_count if move_count > 0 else 0

            print(f"{name:<30} {total_time:<15.3f} {avg_per_move:<15.6f} {move_count:<12}")

        print("\n" + "=" * 80)
        print("GAME-BY-GAME RESULTS")
        print("=" * 80)

        for game in self.game_results:
            winner_str = game['winner'] if game['winner'] else "Draw"
            print(f"Game {game['game_num']:3d}: {game['player1']:<25} vs {game['player2']:<25} "
                  f"| Scores: {game['score1']:3d}-{game['score2']:3d} | Winner: {winner_str}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python tournament_pd.py <player1.py> [player2.py ...] [--games N]")
        print("\nOptions:")
        print("  --games N    Number of games per matchup (default: 5)")
        print("\nExample:")
        print("  python tournament_pd.py games/prisoners_dilemma/pd_player_*.py")
        print("  python tournament_pd.py games/prisoners_dilemma/pd_player_*.py --games 10")
        print("\nNote: Round-robin format - each player competes against all others")
        sys.exit(1)

    # Parse arguments
    games_per_matchup = 5
    player_scripts = []

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--games':
            if i + 1 >= len(sys.argv):
                print("Error: --games requires a number")
                sys.exit(1)
            games_per_matchup = int(sys.argv[i + 1])
            i += 2
        else:
            player_scripts.append(sys.argv[i])
            i += 1

    # Convert to absolute paths and validate
    player_scripts = [os.path.abspath(script) for script in player_scripts]

    for script in player_scripts:
        if not os.path.exists(script):
            print(f"Error: Player script not found: {script}", file=sys.stderr)
            sys.exit(1)

    if len(player_scripts) < 2:
        print("Error: Need at least 2 players for a round-robin tournament", file=sys.stderr)
        sys.exit(1)

    # Run tournament
    tournament = TournamentManager(player_scripts, games_per_matchup)

    try:
        success = tournament.run_tournament()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTournament interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
