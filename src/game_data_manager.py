import os
import json
import stats as statistics_mod


# Constants ensuring that we are guaranteed to receive some semblance of information
GAME_KEY_QUERY = "games"
DEFAULTS_KEY_QUERY = "defaults"
DIFFICULTY_QUERY = "difficulties"
DIFFICULTY_LABEL_QUERY = "difficulty_labels"
DOC_QUERY = "game_docstring"
GAME_VARIATIONS_QUERY = "game_variations"
GAME_UNLOCKED_QUERY = "unlocked_by_default"
# Default stat path
STAT_KEY_QUERY = "stat_items"
# Description of what the stats are in terms of objects
# Must be valid class within the stats package
STAT_CLASS_QUERY = "item_descriptions"
# Controls whether the default statistics will be included
# Supports partial conflicts, I.e, parser is smart enough to recognize that only some keys may require being filled
STAT_INCLUSION_QUERY = "include_statistics"
# Dictates stat class type
STAT_CLS_TYPE = "cls"
# Output messages
STAT_OUTPUT_MSG = "output_msg"
STAT_ORDER_QUERY = "order_by"
STAT_CLASS_SUBSET = (STAT_OUTPUT_MSG, STAT_CLS_TYPE)
# These can be processed without requiring special checks
DEFAULT_QUERIES = (
    GAME_VARIATIONS_QUERY,
    DOC_QUERY,
    GAME_UNLOCKED_QUERY,
)
# We don't enforce the presence of these because they are unique to each game data instance
GAME_DISPLAY_NAME_QUERY = "display_name"


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

    def _fix_diffs(self, name, game):
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
            if sk not in self.game_data[DEFAULTS_KEY_QUERY][DIFFICULTY_LABEL_QUERY]:
                raise ValueError(
                    'Missing difficulty label for "%s" in %s. Either extend default settings, remove this number, or provide a label'
                    % (sk, name)
                )
            else:
                diff_labels[sk] = self.game_data[DEFAULTS_KEY_QUERY][
                    DIFFICULTY_LABEL_QUERY
                ][sk]

        diffs.sort()
        return diffs, diff_labels

    def _fix_stats(self, name, game):
        # If not defined, a game will always have the stats stored under the default setting
        if STAT_KEY_QUERY not in game:
            stats = self.game_data[DEFAULTS_KEY_QUERY][STAT_KEY_QUERY]
        else:
            stats = game[STAT_KEY_QUERY]
            if STAT_CLASS_QUERY not in stats:
                stats[STAT_CLASS_QUERY] = {}

            # Ensure we have the necessary items within `STAT_CLASS_QUERY`
            # Every stat in the file is persistent, meaning that it must have an output message and a class which we could instantiate
            # We do this now because any later adjustments will happen using the information in the default settings, which we somewhat verified earlier
            for k, v in stats[STAT_CLASS_QUERY].items():
                for s in STAT_CLASS_SUBSET:
                    if s not in v:
                        raise ValueError(
                            "Missing %s in %s//%s/%s/%s"
                            % (s, name, STAT_KEY_QUERY, STAT_CLASS_QUERY, k)
                        )

                # Ensure that the stats have valid class types
                if not hasattr(statistics_mod, v[STAT_CLS_TYPE]):
                    raise TypeError(
                        '%s/%s/%s/%s contains an invalid class type, "%s"'
                        % (name, STAT_KEY_QUERY, STAT_CLASS_QUERY, k, v[STAT_CLS_TYPE])
                    )

            if stats.get(STAT_INCLUSION_QUERY, True):
                for k in [
                    i
                    for i in self.game_data[DEFAULTS_KEY_QUERY][STAT_KEY_QUERY][
                        STAT_CLASS_QUERY
                    ]
                    if i not in stats[STAT_CLASS_QUERY]
                ]:
                    stats[STAT_CLASS_QUERY][k] = self.game_data[DEFAULTS_KEY_QUERY][
                        STAT_KEY_QUERY
                    ][STAT_CLASS_QUERY][k]

        return stats

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
        for k in (
            DIFFICULTY_QUERY,
            DIFFICULTY_LABEL_QUERY,
            STAT_KEY_QUERY,
            *DEFAULT_QUERIES,
        ):
            if k not in self.game_data[DEFAULTS_KEY_QUERY]:
                raise ValueError(
                    "Missing value for default setting. Should be stored under %s/%s"
                    % (DEFAULTS_KEY_QUERY, k)
                )

        for name, game in self.game_data[GAME_KEY_QUERY].items():
            diffs, diff_labels = self._fix_diffs(name, game)
            game[DIFFICULTY_QUERY] = diffs
            game[DIFFICULTY_LABEL_QUERY] = diff_labels

            stats = self._fix_stats(name, game)
            game[STAT_KEY_QUERY] = stats

            # Handle misc stuff
            for k in DEFAULT_QUERIES:
                if not game.get(k, None):
                    game[k] = self.game_data[DEFAULTS_KEY_QUERY][k]

    def gather_unlocked_game_stats(self, game):
        stat_lst = {}
        for k, v in game[STAT_KEY_QUERY][STAT_CLASS_QUERY].items():
            stat_lst[k] = getattr(statistics_mod, v[STAT_CLS_TYPE])()
        return stat_lst

    def gather_unlocked_game_info(self, game, variation, difficulty):
        varname = game[GAME_VARIATIONS_QUERY][variation]
        diffnum = game[DIFFICULTY_QUERY][difficulty]
        dct = {GAME_VARIATIONS_QUERY: {varname: [diffnum]}}
        stat_lst = self.gather_unlocked_game_stats(game)

        return dct, {GAME_VARIATIONS_QUERY: {varname: {str(difficulty): stat_lst}}}

    def gather_unlocked_games(self):
        return_dict = {"games": {}, "stats": {}}
        for name in self.game_data[GAME_KEY_QUERY]:
            if not self.game_data[GAME_KEY_QUERY][name].get(GAME_UNLOCKED_QUERY, False):
                continue

            # We, a bit arbitrarily, unlock the first variation for each unlocked ggame
            # We also unlock a single difficulty
            game, statistics = self.gather_unlocked_game_info(
                self.game_data[GAME_KEY_QUERY][name], 0, 0
            )
            return_dict["games"][name] = game
            return_dict["stats"][name] = statistics

        return return_dict

    def generate_new_player_data(self):
        # We just gather unlocked games, for now
        # This will possibly be extended as more stuff gets added
        unlocked_games = self.gather_unlocked_games()
        return unlocked_games

    def fetch_game(self, game):
        if game not in self.game_data[GAME_KEY_QUERY]:
            raise ValueError('The selected game, "%s", does not exist' % game)
        return self.game_data[GAME_KEY_QUERY][game]

    def fetch_game_display_name(self, game):
        return self.fetch_game(game).get(GAME_DISPLAY_NAME_QUERY, game).capitalize()

    def fetch_game_doc(self, game):
        return self.fetch_game(game)[DOC_QUERY]

    def fetch_game_difficulty_label(self, game, diff):
        return self.fetch_game(game)[DIFFICULTY_LABEL_QUERY][str(diff)]

    def fetch_game_statistic_display_order(self, game):
        stats = self.fetch_game(game)[STAT_KEY_QUERY][STAT_CLASS_QUERY]
        return stats.get(STAT_ORDER_QUERY, sorted(stats.keys()))

    def fetch_game_statistic_display_msg(self, game, stat):
        stats = self.fetch_game(game)[STAT_KEY_QUERY][STAT_CLASS_QUERY]
        return stats[stat][STAT_OUTPUT_MSG]
