import os
import json


# Constants ensuring that we are guaranteed to receive some semblance of information
GAME_KEY_QUERY = "games"
DEFAULTS_KEY_QUERY = "defaults"
DIFFICULTY_QUERY = "difficulties"
DIFFICULTY_LABEL_QUERY = "difficulty_labels"
DOC_QUERY = "game_docstring"
GAME_VARIATIONS_QUERY = "game_variations"
GAME_UNLOCKED_QUERY = "unlocked_by_default"
# These can be processed without requiring special checks
DEFAULT_QUERIES = (
    GAME_VARIATIONS_QUERY,
    DOC_QUERY,
    GAME_UNLOCKED_QUERY,
)


class GameDataManager:
    """A class responsible for interpreting info.json and responding to any future user queries about the unlocked data"""

    def __init__(self):
        self.game_data = {}

    def load(self, data_filepath):
        if not os.path.isfile(data_filepath):
            raise ValueError("Invalid game data path provided, %s" % data_filepath)

        with open(data_filepath, "r") as f:
            self.game_data = json.loads(f.read())

        # Account for missing or empty values
        self.fix_self()

    def fix_self(self):
        if GAME_KEY_QUERY not in self.game_data:
            raise ValueError(
                "Missing game storage. Should be stored under %s" % GAME_KEY_QUERY
            )

        if DEFAULTS_KEY_QUERY not in self.game_data:
            raise ValueError(
                "Missing default game parameters. Should be stored under %s"
                % DEFAULTS_KEY_QUERY
            )

        # Ensure default settings exist because the next fix patches the missing values
        for k in (DIFFICULTY_QUERY, DIFFICULTY_LABEL_QUERY, *DEFAULT_QUERIES):
            if k not in self.game_data[DEFAULTS_KEY_QUERY]:
                raise ValueError(
                    "Missing value for default setting. Should be stored under %s/%s"
                    % (DEFAULTS_KEY_QUERY, k)
                )

        for name, game in self.game_data[GAME_KEY_QUERY].items():
            # We handle difficulty and difficulty labels first because they require special intervention than just a raw replace
            # A game has a valid set of difficulties for the following cases
            # 1. It doesn't have the DIFFICULTY_QUERY key and it either doesn't have the DIFFICULTY_LABEL_QUERY or DIFFICULTY_LABEL_QUERY matches all of the integers accessed via DIFFICULTY_QUERY
            # 2. It has the "difficulties" key but does not have DIFFICULTY_LABEL_QUERY. In this case, difficulty integers must be within DEFAULTS_KEY_QUERY/DIFFICULTY_LABEL_QUERY
            # 3. it does have the DIFFICULTY_QUERY, and the integers are either in DEFAULTS_KEY_QUERY/DIFFICULTY_QUERY or DIFFICULTY_LABEL_QUERY
            diffs = game.get(DIFFICULTY_QUERY, [])
            diff_labels = game.get(DIFFICULTY_LABEL_QUERY, {})
            if len(diffs) == 0:
                diffs = self.game_data[DEFAULTS_KEY_QUERY][DIFFICULTY_QUERY]
            if len(diff_labels) == 0:
                diff_labels = self.game_data[DEFAULTS_KEY_QUERY][DIFFICULTY_LABEL_QUERY]

            for k in [i for i in diffs if str(i) not in diff_labels]:
                sk = str(k)
                if (
                    sk
                    not in self.game_data[DEFAULTS_KEY_QUERY][
                        DIFFICULTY_LABEL_QUERY
                    ]
                ):
                    raise ValueError(
                        'Missing difficulty label for "%s" in %s. Either extend default settings, remove this number, or provide a label'
                        % (sk, name)
                    )
                else:
                    diff_labels[sk] = self.game_data[DEFAULTS_KEY_QUERY][
                        DIFFICULTY_LABEL_QUERY
                    ][sk]

            diffs.sort()
            game[DIFFICULTY_QUERY] = diffs
            game[DIFFICULTY_LABEL_QUERY] = diff_labels

            # Handle other, less complicated matters
            for k in DEFAULT_QUERIES:
                if not game.get(k, None):
                    game[k] = self.game_data[DEFAULTS_KEY_QUERY][k]

    def gather_unlocked_games(self):
        return_dict = {}
        for name, game in self.game_data[GAME_KEY_QUERY].items():
            if not game.get(GAME_UNLOCKED_QUERY, False):
                continue

            # We, a bit arbitrarily, unlock the first variation for each unlocked ggame
            # We also unlock a single difficulty
            varname = game[GAME_VARIATIONS_QUERY][0]
            diffnum = game[DIFFICULTY_QUERY][0]
            return_dict[name] = {GAME_VARIATIONS_QUERY: {varname: [diffnum]}}

        return return_dict

    def generate_new_player_data(self):
        # We just gather unlocked games, for now
        # This will possibly be extended as more stuff gets added
        unlocked_games = self.gather_unlocked_games()
        return unlocked_games
