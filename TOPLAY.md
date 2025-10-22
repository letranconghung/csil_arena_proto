To do: modify the file `pd_player_template.py`. A few things to note:
- 1 instance of the player class will be sustained throughout each game, so you can do some tracking
- modify `on_game_start` to do any initialization
- modify `on_your_turn` for turn logic
- you shouldn't be editing `on_game_over`


**CAUTION**: USE `debug` to debug, NOT `print`.

Run the following command from the repo root to play against another bot.

``
python run_pd.py games/pd/pd_player_template.py games/pd/pd_player_always_cooperate.py
``

Run with ``--verbose`` flag to see your debug messages.

``
python run_pd.py games/pd/pd_player_template.py games/pd/pd_player_always_cooperate.py --verbose
``

To see how your bot will perform in a tournament, you can run

``
python tournament_pd.py games/pd/pd_player_*.py --games 3
``

which runs a tournament among all the players. The `_*` unpacks to a list, so if you want to simulate having 2 Maanavs (always-defector), you can run

``
python tournament_pd.py games/pd/pd_player_*.py games/pd/pd_player_always_defect.py --games 3
``
and so on.