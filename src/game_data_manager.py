import stats as statistics_mod
from constants import (
    DIFFICULTY,
    DIFFICULTY_INCLUDE,
    DOC,
    GAME_DISPLAY_NAME,
    GAME_STATS,
    GAME_STAT_SETTINGS,
    GAME_UNLOCKED,
    GAME_VARIATIONS,
    GAME_VARIATION_INCLUSION,
    STAT_CLS_TYPE,
    STAT_INCLUSION,
    STAT_ORDER,
    STAT_OUTPUT_MSG,
)


class GameDataManager:
    """A class responsible for answering questions about game data"""

    def __init__(self):
        self.default_settings = {}
        self.games = {}
        self.game_stats = {}
        self.game_stat_settings = {}

    def set_default_settings(self, settings):
        self.default_settings = settings

    def set_games(self, games):
        # Go through and separate games from game stats to simplify queries
        for k, v in games.items():
            if GAME_STATS in v:
                self.game_stats[k] = v.pop(GAME_STATS)
            if GAME_STAT_SETTINGS in v:
                self.game_stat_settings[k] = v.pop(GAME_STAT_SETTINGS)

        self.games = games

    def gather_unlocked_game_stats(self, game_name, init_cls=True):
        stat_dict = {}
        for s, t in self.fetch_game_stats(game_name).items():
            # `t` is guaranteed to have any queried keys due to parser constraints
            cls = t[STAT_CLS_TYPE]
            if not hasattr(statistics_mod, cls):
                raise RuntimeError(
                    "Cannot find the indicated class type, %s, for %s/%s"
                    % (cls, game_name, s)
                )
            stat_obj = getattr(statistics_mod, cls)
            stat_dict[s] = stat_obj() if init_cls else stat_obj

        return stat_dict

    def gather_unlocked_game_info(self, game_name, variation, difficulty):
        varname = self.fetch_game_variation_label(game_name, variation)
        # Although we don't need it, this serves as an error check and doesn't cost anything
        # Probably convert this to game_difficulty_exists at some point
        diff_label = self.fetch_game_difficulty_label(game_name, difficulty)
        game_dict = {GAME_VARIATIONS: {varname: [difficulty]}}
        return game_dict

    def gather_unlocked_games(self, excluded_games=None):
        games = {}
        statistics = {}
        if excluded_games is not None:
            game_keys = [k for k in self.games if k not in excluded_games]
        else:
            game_keys = list(self.games)

        for g in game_keys:
            # We should probably do some error checks here for empty diffs / variations and such
            if self.games[g].get(GAME_UNLOCKED, self.default_settings[GAME_UNLOCKED]):
                # We arbitrarily unlock first variation / difficulty
                games[g] = self.gather_unlocked_game_info(g, 0, 0)
                varname = self.fetch_game_variation_label(g, 0)
                statistics[g] = {
                    GAME_VARIATIONS: {varname: {0: self.gather_unlocked_game_stats(g)}}
                }

        return games, statistics

    def generate_new_player_data(self):
        return self.gather_unlocked_games()

    def _merge_unique_data(
        self, first_data, second_data, should_not_be_empty=True, except_msg=""
    ):
        difference = {k: v for k, v in second_data.items() if k not in first_data}
        new_data = {**first_data, **difference}
        if should_not_be_empty and len(new_data) == 0:
            raise ValueError(except_msg)
        return new_data

    def fetch_game(self, game_name):
        if game_name not in self.games:
            raise KeyError('The provided game, "%s", does not exist' % game_name)
        return self.games[game_name]

    def fetch_game_stats(self, game_name):
        stats = self.game_stats.get(game_name, {})
        if self.fetch_game_stat_settings(game_name).get(
            STAT_INCLUSION, self.default_settings[GAME_STAT_SETTINGS][STAT_INCLUSION]
        ):
            diff_data = self.default_settings[GAME_STATS]
        else:
            diff_data = {}
        return self._merge_unique_data(stats, diff_data, False)

    def fetch_game_stat_settings(self, game_name):
        return self.game_stat_settings.get(game_name, {})

    def fetch_game_display_name(self, game_name):
        return self.fetch_game(game_name).get(GAME_DISPLAY_NAME, game_name)

    def fetch_game_doc(self, game_name):
        return self.fetch_game(game_name).get(DOC, self.default_settings[DOC])

    def fetch_game_variations(self, game_name):
        e_msg = (
            "Encountered empty variation list for %s. Either provide variations or allow for inclusion of default variations via %s"
            % (game_name, GAME_VARIATION_INCLUSION)
        )
        game = self.fetch_game(game_name)
        variations = game.get(GAME_VARIATIONS, {})
        if game.get(
            GAME_VARIATION_INCLUSION, self.default_settings[GAME_VARIATION_INCLUSION]
        ):
            diff_data = self.default_settings[GAME_VARIATIONS]
        else:
            diff_data = {}
        return self._merge_unique_data(variations, diff_data, except_msg=e_msg)

    def fetch_game_variation_label(self, game_name, variation):
        variations = self.fetch_game_variations(game_name)
        if variation not in variations:
            raise KeyError(
                "The provided variation for %s, %s, does not exist"
                % (game_name, variation)
            )
        return variations[variation]

    def fetch_difficulties(self, game_name):
        e_msg = (
            "Encountered empty difficulty list for %s. Either provide difficulties or allow for inclusion of default difficulties via %s"
            % (game_name, DIFFICULTY_INCLUDE)
        )
        game = self.fetch_game(game_name)
        diffs = game.get(DIFFICULTY, {})
        if game.get(DIFFICULTY_INCLUDE, self.default_settings[DIFFICULTY_INCLUDE]):
            diff_data = self.default_settings[DIFFICULTY]
        else:
            diff_data = {}
        return self._merge_unique_data(diffs, diff_data, except_msg=e_msg)

    def fetch_game_difficulty_label(self, game_name, diff):
        diffs = self.fetch_difficulties(game_name)
        if diff not in diffs:
            raise KeyError(
                "The provided difficulty for %s, %s, does not exist" % (game_name, diff)
            )
        return diffs[diff]

    def fetch_game_statistic_display_order(self, game_name):
        return self.fetch_game_stat_settings(game_name).get(STAT_ORDER, [])

    def fetch_game_statistic_display_msg(self, game_name, stat):
        stats = self.fetch_game_stats(game_name)
        if stat not in stats:
            raise KeyError("No stat matching %s was found for %s" % (stat, game_name))
        return stats[stat][STAT_OUTPUT_MSG]
